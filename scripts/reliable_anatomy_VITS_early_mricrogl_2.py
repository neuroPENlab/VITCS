import gl
gl.resetdefaults()

gl.loadimage('spm152')
gl.backcolor(255, 255, 255)

# UNC 0.01 POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_early/reliable_anatomy/UNC01_pos_prunedfdr05_pos.nii.gz')
gl.colorname(1,"8redyell")
gl.minmax(1, 0.9, 2)

# UNC 0.01 NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_early/reliable_anatomy/UNC01_pos_prunedfdr05_neg.nii.gz')
gl.colorname(2,"electric_blue")
gl.minmax(2, 0.8, 2)

# UNC 0.001 POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_early/reliable_anatomy/UNC001_pos_prunedfdr05_pos.nii.gz')
gl.colorname(3,"8redyell")
gl.minmax(3, 0, 1.8)

# UNC 0.001 NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_early/reliable_anatomy/UNC001_pos_prunedfdr05_neg.nii.gz')
gl.colorname(4,"electric_blue")
gl.minmax(4, 0, 2.2)

# FDR 0.05 POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_early/reliable_anatomy/fdr05_pos.nii.gz')
gl.colorname(5,"8redyell")
gl.minmax(5, 0, 1)

# FDR 0.05 NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_early/reliable_anatomy/fdr05_neg.nii.gz')
gl.colorname(6,"electric_blue")
gl.minmax(6, 0, 1.3)

gl.mosaic("A H 0.08 V 0.08 52 22 17 -9 S H 0.08 V 0.08 -44 -34 -9.5 C H 0.08 V 0.08 48 -28")
#gl.meshangle(45, 30, 0)  # rota el render

#gl.savebmp('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/__FIGURES_ARTICLE/mosaic.png')