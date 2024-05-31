# release-branches
Manage the release branches for RBC repositories

The code here manages the creation and sharing of release branches/tags
for RBC data repositories.

Each of the RBC repos has a set of branches that include data for
scans that pass a set of criteria. The branches are:

 * `complete-pass`: Structural and BOLD data have passed QC
 * `complete-artifact`: Structural data can be "Pass" or "Artifact", BOLD is "Pass"
 * `warning-fail`: Contains all the potential data - you'll have to explain why you chose this in any resulting work.

## Making a release branch

The process of creating release branches/tags is done There need to be 2 tsv files for each project

 1. The Structural QC tsv
 2. The BOLD QC tsv

These are consistently named across repos so th