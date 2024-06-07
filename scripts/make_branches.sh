#!/bin/bash

SCRIPT="/cbica/projects/RBC/software/release-branches/scripts/do_release.py"

STUDY=$1
RELEASE=$2

WORK_DIR="${TMP}/rbc-release"
mkdir -p ${WORK_DIR}
cd ${WORK_DIR}

git clone git@github.com:ReproBrainChart/${STUDY}_FreeSurfer.git
git clone git@github.com:ReproBrainChart/${STUDY}_CPAC.git

python \
    -m pdb \
    ${SCRIPT} \
    ${STUDY} \
    ${WORK_DIR}/${STUDY}_FreeSurfer \
    ${WORK_DIR}/${STUDY}_CPAC \
    ${RELEASE} \
    --verbose
