#!/usr/bin/env bash

basedir="<PATH_TO_PROJECT>" # <-- EDIT THIS
scritsdir="${basedir}/scripts/utils"
outputdir="${basedir}/results/VITCS_early_results/reliable_anatomy"

# (1) Separate positive and negative clusters and binarize
bash ${scritsdir}/process_reliable_anatomy.sh  "${outputdir}/VITCS_bootstrap_fdr05.nii" \
												"${outputdir}/VITCS_bootstrap_fdr05_pos_bin.nii" \
 												"${outputdir}/VITCS_bootstrap_fdr05_neg_bin.nii"

bash ${scritsdir}/process_reliable_anatomy.sh  "${outputdir}/VITCS_bootstrap_unc001.nii"  \
												"${outputdir}/VITCS_bootstrap_unc001_pos_bin.nii" \
		 										"${outputdir}/VITCS_bootstrap_unc001_neg_bin.nii"

bash ${scritsdir}/process_reliable_anatomy.sh  "${outputdir}/VITCS_bootstrap_unc01.nii"  \
												"${outputdir}/VITCS_bootstrap_unc01_pos_bin.nii" \
		 										"${outputdir}/VITCS_bootstrap_unc01_neg_bin.nii"

# (2) Prune FDR-corrected clusters from the uncorrected maps

bash ${scritsdir}/cluster_prunning.sh "${outputdir}/VITCS_bootstrap_unc001_pos_bin.nii" \
										"${outputdir}/VITCS_bootstrap_fdr05_pos_bin.nii" \
										"${outputdir}/UNC001_prunedfdr05_pos.nii.gz" 0.00 1

bash ${scritsdir}/cluster_prunning.sh "${outputdir}/VITCS_bootstrap_unc001_neg_bin.nii" \
										"${outputdir}/VITCS_bootstrap_fdr05_neg_bin.nii" \
										"${outputdir}/UNC001_prunedfdr05_neg.nii.gz" 0.00 1

bash ${scritsdir}/cluster_prunning.sh "${outputdir}/VITCS_bootstrap_unc01_pos_bin.nii" \
										"${outputdir}/VITCS_bootstrap_fdr05_pos_bin.nii" \
										"${outputdir}/UNC01_prunedfdr05_pos.nii.gz" 0.00 1

bash ${scritsdir}/cluster_prunning.sh "${outputdir}/VITCS_bootstrap_unc01_neg_bin.nii" \
										"${outputdir}/VITCS_bootstrap_fdr05_neg_bin.nii" \
										"${outputdir}/UNC01_prunedfdr05_neg.nii.gz" 0.00 1