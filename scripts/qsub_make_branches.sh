#!/bin/bash
RELEASE=0.1
STUDIES="CCNP PNC NKI BHRC HBN"

for STUDY in ${STUDIES}
do
    qsub ${PWD}/make_branches.sh ${STUDY} ${RELEASE}
done
