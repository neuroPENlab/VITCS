import gl
gl.resetdefaults()

gl.loadimage('spm152')
gl.backcolor(255, 255, 255)

# Univariate POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/Fear_Conditioning_MegaAnalysis_NormModelling/RESULTS/mega_analysis_numerical_source_data/1_main_contrast_cs+VScs-/52811654_map_pos.nii.gz')
#gl.colorname(1, "1red")
#gl.minmax(1, 0, 10)
#gl.opacity(1, 50)
gl.colorname(1, "magma")
gl.minmax(1, 0, 15)
gl.opacity(1, 75)

# Univariate NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/Fear_Conditioning_MegaAnalysis_NormModelling/RESULTS/mega_analysis_numerical_source_data/1_main_contrast_cs+VScs-/52811651_map_neg.nii.gz')
#gl.colorname(2, "3blue")
#gl.minmax(2, 0, 2)
#gl.opacity(2, 50)
gl.colorname(2, "2green")
gl.minmax(2, 0, 10)
gl.opacity(2, 70)

# UNC 0.01 POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/UNC01_pos_prunedfdr05_pos.nii.gz')
gl.colorname(3, "8redyell")
gl.minmax(3, 0.9, 2)

# UNC 0.01 NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/UNC01_pos_prunedfdr05_neg.nii.gz')
gl.colorname(4, "electric_blue")
gl.minmax(4, 0.8, 2)

# UNC 0.001 POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/UNC001_pos_prunedfdr05_pos.nii.gz')
gl.colorname(5, "8redyell")
gl.minmax(5, 0, 1.8)

# UNC 0.001 NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/UNC001_pos_prunedfdr05_neg.nii.gz')
gl.colorname(6, "electric_blue")
gl.minmax(6, 0, 2.2)

# FDR 0.05 POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/fdr05_pos.nii.gz')
gl.colorname(7, "8redyell")
gl.minmax(7, 0, 1)

# FDR 0.05 NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/fdr05_neg.nii.gz')
gl.colorname(8, "electric_blue")
gl.minmax(8, 0, 1.3)

gl.mosaic("A H -0.08 V 0 31.5 30 24 17 0.5 -21; S H -0.08 V 0 -48 -39 -6.4 3.1 50.3 59; C H -0.08 V 0 38.2 -2.3 -12 -16.4 -38")
