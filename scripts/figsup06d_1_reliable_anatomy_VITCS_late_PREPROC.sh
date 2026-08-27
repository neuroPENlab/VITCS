#!/usr/bin/env bash

basedir="<PATH_TO_PROJECT>" # <-- EDIT THIS
scritsdir="${basedir}/scripts/utils"
outputdir="${basedir}/results/VITCS_late_results/reliable_anatomy"

# (1) Separate positive and negative clusters and binarize
bash ${scritsdir}/process_reliable_anatomy.sh  "${outputdir}/VITCS_bootstrap_unc001.nii"  \
												"${outputdir}/VITCS_bootstrap_unc001_pos_bin.nii" \
		 										"${outputdir}/VITCS_bootstrap_unc001_neg_bin.nii"

bash ${scritsdir}/process_reliable_anatomy.sh  "${outputdir}/VITCS_bootstrap_unc01.nii"  \
												"${outputdir}/VITCS_bootstrap_unc01_pos_bin.nii" \
		 										"${outputdir}/VITCS_bootstrap_unc01_neg_bin.nii"

# (2) Prune FDR-corrected clusters from the uncorrected maps
bash ${scritsdir}/cluster_prunning.sh "${outputdir}/VITCS_bootstrap_unc01_pos_bin.nii" \
										"${outputdir}/VITCS_bootstrap_unc001_pos_bin.nii" \
										"${outputdir}/UNC01_pruned001_pos.nii.gz" 0.00 1

bash ${scritsdir}/cluster_prunning.sh "${outputdir}/VITCS_bootstrap_unc01_neg_bin.nii" \
										"${outputdir}/VITCS_bootstrap_unc001_neg_bin.nii" \
										"${outputdir}/UNC01_pruned001_neg.nii.gz" 0.00 1