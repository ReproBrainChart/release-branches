#!/usr/bin/env python

"""
get a list of files to remove from a branch in order to make a release

"""
import argparse
import logging
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

NO_SES_STUDIES = {
    "CCNP": 1,
    "PNC": "PNC1",
}


def get_things_to_delete(study_name, fs_dir, bold_dir):
    """Create dataframes that specify which modalities fail QC thresholds

    Parameters:
    -----------

    study_name: str
        The name of the study to create dataframes for

    fs_dir: Path
        Path where the FreeSurfer derivatives live

    bold_dir: Path
        Path where the BOLD data lives

    Returns:
    --------

    t1_artifact: pd.DataFrame
        subjects/sessions with artifact T1s

    t1_fail: pd.DataFrame
        subjects/sessions where T1s failed QC

    bold_fail: pd.DataFrame
        Bold scans that have failed QC

    """
    # Load the Structural QC

    t1_qc_df = pd.read_csv(fs_dir / f"study-{study_name}_desc-T1_qc.tsv", sep="\t")
    if study_name in NO_SES_STUDIES:
        t1_qc_df["session_id"] = NO_SES_STUDIES[study_name]

    # Load the BOLD QC
    bold_qc_df = pd.read_csv(
        bold_dir / "cpac_RBCv0" / f"study-{study_name}_desc-functional_qc.tsv", sep="\t"
    )

    # Create a list of files to delete from the different branches
    t1_artifact = t1_qc_df[t1_qc_df["qc_determination"] == "Artifact"][
        ["participant_id", "session_id"]
    ]
    t1_fail = t1_qc_df[t1_qc_df["qc_determination"] == "Fail"][
        ["participant_id", "session_id"]
    ]

    # Get a list of bold failures
    bold_fail = bold_qc_df[bold_qc_df["fmriExclude"] > 0][
        ["participant_id", "session_id", "task", "run", "acq"]
    ]

    return t1_artifact, t1_fail, bold_fail


def safe_run(cmd):
    """use subprocess.run and exit if there is a failure"""
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    cmdtxt = " ".join(cmd)
    logging.info("RUNNING:\n\t" + cmdtxt)  # will not print anything
    if result.returncode > 0:
        print("stderr:", result.stderr)
        print("stdout:", result.stdout)
        raise Exception("\n\nError running:\n\n" + cmdtxt)


def safe_delete_batch(files_to_delete, batch_size=5000):
    """Sometimes the list of files is too long for git. So this
    function will split them into batches of 1mil"""
    if not files_to_delete:
        logging.info("No files to git rm.")
        return

    n_chunks = len(files_to_delete) // batch_size + 1
    chunks = np.array_split(files_to_delete, n_chunks)
    logging.info(f"git rm-ing {len(files_to_delete)} files in {n_chunks} batches")
    for chunk in chunks:
        safe_run(["git", "rm", "-rf"] + chunk.tolist())


def clean_dataset(study_name, tag, data_dir, t1_artifact, t1_fail, bold_fail=None):
    """

    Steps:
    ------

    1. Check out the complete-artifact branch
    2. Delete all of the Fail sessions
    3. Commit, tag and push
    4. Check out the complete-pass branch
    5. Delete all the Artifact sessions
    6. Commit, tag and push

    """

    os.chdir(data_dir)
    safe_run(["git", "checkout", "main"])

    warning_branch = f"warning-fail-{tag}"
    artifact_branch = f"complete-artifact-{tag}"
    pass_branch = f"complete-pass-{tag}"

    doing_bold = bold_fail is not None

    def get_dir_to_delete(participant_id, session_id):
        if not doing_bold:
            inner_dir = "freesurfer"
        else:
            inner_dir = "cpac_RBCv0"

        participant_dir = (
            f"sub-{participant_id}" if "-" not in str(participant_id) else participant_id
        )

        if study_name in NO_SES_STUDIES:
            base_dir = data_dir / inner_dir / participant_dir
        else:
            if not doing_bold:
                base_dir = data_dir / inner_dir / f"{participant_dir}_ses-{session_id}"
            else:
                base_dir = data_dir / inner_dir / participant_dir / f"ses-{session_id}"

        if not base_dir.exists():
            logging.warning(f"missing {base_dir}")
            return None
        return base_dir

    def delete_bold_files(row):
        """The subject may have already been deleted via t1 qc,
        so only glob if the directory exists."""
        participant_bids = (
            f"sub-{row.participant_id}"
            if "-" not in str(row.participant_id)
            else row.participant_id
        )
        session_bids = f"ses-{row.session_id}"

        base_dir = data_dir / "cpac_RBCv0" / participant_bids / session_bids
        if not base_dir.exists():
            return

        # sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>][_part-<mag|phase|real|imag>][_chunk-<index>]_bold.
        search = "*"
        search_zpad = "*"
        if row.task is not None:
            search += f"task-{row.task}*"
            search_zpad += f"task-{row.task}*"
        if not (np.isnan(row.acq) or row.acq is None):
            search += f"acq-{row.acq}*"
            search_zpad += f"acq-{row.acq}*"
        if not (np.isnan(row.run) or row.run is None):
            search += f"run-{row.run}*"
            search_zpad += f"run-{row.run:02}*"
        bold_files_to_delete = list(base_dir.rglob(search)) + list(
            base_dir.rglob(search_zpad)
        )
        if not bold_files_to_delete:
            logging.warning(f"No files found for {row}")
        return list(map(str, bold_files_to_delete))

    def commit_and_push(branchname, msg, do_commit=False):
        tagname = f"release-{branchname}"
        if do_commit:
            safe_run(["git", "commit", "-m", f"'{msg}'"])
        # XXX UNCOMMENT
        # safe_run(["git", "tag", tagname])
        # safe_run(["git", "push", "origin", branchname])
        # safe_run(["git", "push", "origin", tagname])

    safe_run(["git", "checkout", "-b", warning_branch])
    commit_and_push(warning_branch, "update warning branch", do_commit=False)

    # Update the complete-artifact branch
    safe_run(["git", "checkout", "-b", artifact_branch])
    fail_dirs_to_delete = []
    for _, row in tqdm(t1_fail.iterrows(), total=t1_fail.shape[0]):
        base_dir = get_dir_to_delete(row.participant_id, row.session_id)
        if base_dir is not None:
            fail_dirs_to_delete.append(str(base_dir))

    logging.info(f"Deleting {len(fail_dirs_to_delete)} T1w-fail dirs")
    safe_delete_batch(fail_dirs_to_delete)

    # Delete any BOLD files if requested
    bold_files_to_delete = []
    if doing_bold:
        for _, row in tqdm(bold_fail.iterrows(), total=bold_fail.shape[0]):
            relevant_bold_files = delete_bold_files(row)
            if relevant_bold_files:
                bold_files_to_delete.extend(relevant_bold_files)
                safe_delete_batch(relevant_bold_files)

        logging.info(f"Deleting {len(bold_files_to_delete)} BOLD-related files")

    fail_plus_bold_to_del = fail_dirs_to_delete + bold_files_to_delete
    commit_and_push(
        artifact_branch,
        "remove qc-fail sessions",
        do_commit=len(fail_plus_bold_to_del) > 0,
    )

    # Update the complete-pass branch
    safe_run(["git", "checkout", "-b", pass_branch])
    artifact_dirs_to_delete = []
    for _, row in tqdm(t1_artifact.iterrows(), total=t1_artifact.shape[0]):
        base_dir = get_dir_to_delete(row.participant_id, row.session_id)
        if base_dir is not None:
            artifact_dirs_to_delete.append(str(base_dir))
    logging.info(f"Deleting {len(artifact_dirs_to_delete)} T1w-artifact dirs")
    safe_delete_batch(artifact_dirs_to_delete)

    commit_and_push(
        pass_branch,
        "remove qc-artifact sessions",
        do_commit=len(artifact_dirs_to_delete) > 0,
    )


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "study_name",
        choices=["CCNP", "BHRC", "NKI", "HBN", "PNC"],
        help="Which RBC study are you working with",
    )
    parser.add_argument(
        "freesurfer_dir",
        type=Path,
        help="Path to the study's FreeSurfer derivative dataset",
    )
    parser.add_argument(
        "bold_dir", type=Path, help="Path to the study's CPAC derivative dataset"
    )
    parser.add_argument("tag", help="Tag for the versioned branch")
    parser.add_argument("--verbose", action="store_true", default=False)
    return parser


if __name__ == "__main__":
    args = get_parser().parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    t1_artifact, t1_fail, bold_fail = get_things_to_delete(
        args.study_name, args.freesurfer_dir, args.bold_dir
    )

    # create branches in the anatomical derivatives
    clean_dataset(args.study_name, args.tag, args.freesurfer_dir, t1_artifact, t1_fail)

    # create branches in the bold derivatives
    clean_dataset(
        args.study_name, args.tag, args.bold_dir, t1_artifact, t1_fail, bold_fail
    )
