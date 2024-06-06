#!/bin/bash
RELEASE=0.0.1
STUDIES="CCNP PNC NKI BHRC HBN"
WORK_DIR="/cbica/comp_space/RBC/concat"

mkdir -p ${WORK_DIR}

cd ${WORK_DIR}
for study in ${STUDIES}
do
    datalad clone git@github.com:ReproBrainChart/${study}_FreeSurfer.git
    datalad clone git@github.com:ReproBrainChart/${study}_CPAC.git

done
