#!/bin/bash
#$ -S /bin/bash
#$ -l h_vmem=32G
#$ -l tmpfree=100G
#$ -l h_rt=48:00:00
set -e -x

SCRIPT="/cbica/projects/RBC/software/release-branches/scripts/do_release.py"

STUDY=$1
RELEASE=$2

WORK_DIR="${TMP}/rbc-release"
mkdir -p "${WORK_DIR}"
cd "${WORK_DIR}"

git clone "git@github.com:ReproBrainChart/${STUDY}_FreeSurfer.git"
git clone "git@github.com:ReproBrainChart/${STUDY}_CPAC.git"

python \
    ${SCRIPT} \
    "${STUDY}" \
    "${WORK_DIR}/${STUDY}_FreeSurfer" \
    "${WORK_DIR}/${STUDY}_CPAC" \
    "${RELEASE}" \
    --verbose

rm -rf "${WORK_DIR}"
