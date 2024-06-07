#!/bin/bash
RELEASE=0.0.1
STUDIES="CCNP PNC NKI BHRC HBN"
WORK_DIR="/cbica/comp_space/RBC/release"
SCRIPT="$PWD/do_release.py"

mkdir -p ${WORK_DIR}

cd ${WORK_DIR}
for study in ${STUDIES}
do
    git clone git@github.com:ReproBrainChart/${study}_FreeSurfer.git
    git clone git@github.com:ReproBrainChart/${study}_CPAC.git

#    python \
#        -m pdb \
#        ${SCRIPT} \
#        ${study} \
#        ${WORK_DIR}/${study}_FreeSurfer \
#        ${WORK_DIR}/${study}_CPAC \
#        ${RELEASE} \
#        --verbose
#    rm -rf ${study}_FreeSurfer ${study}_CPAC.git

done
