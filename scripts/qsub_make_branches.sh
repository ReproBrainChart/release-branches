#!/bin/bash

RELEASE=0.1
STUDIES="CCNP PNC NKI BHRC HBN"

LOGDIR="/cbica/projects/RBC/release/${RELEASE}-logs"
mkdir -p "${LOGDIR}"

for STUDY in ${STUDIES}
do
    qsub \
        -N "${STUDY}-${RELEASE}" \
        -e "${LOGDIR}" \
        -o "${LOGDIR}" \
        "${PWD}/make_branches.sh" "${STUDY}" "${RELEASE}"
done
