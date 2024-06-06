#!/bin/bash

# Update
rm code/concatenate_bold_qc_files.py
cd code
wget https://raw.githubusercontent.com/ReproBrainChart/release-branches/main/scripts/concatenate_bold_qc_files.py
cd ..

echo 'cpac_RBCv0/*.tsv annex.largefiles=nothing' >> .gitattributes
git add .gitattributes code/concatenate_bold_qc_files.py
git commit -m "keep concatenated tsvs in git"
git push origin main

ulimit -s 8192
datalad get cpac_RBCv0/sub-*/ses-*/func/*reg-36Parameter_desc-xcp_quality.tsv
datalad get cpac_RBCv0/sub-*/ses-*/func/*desc-FDJenkinson_motion.1D
datalad run \
  -i 'code/concatenate_bold_qc_files.py' \
  -o cpac_RBCv0/study-${study}_desc-functional_qc.tsv \
  --explicit \
  "python ./code/concatenate_bold_qc_files.py ${study} --bold-dir ${PWD}"


