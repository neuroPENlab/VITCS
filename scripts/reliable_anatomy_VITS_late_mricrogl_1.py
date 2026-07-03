import gl
gl.resetdefaults()

gl.loadimage('spm152')
gl.backcolor(255, 255, 255)

# UNC 0.01 POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_late/reliable_anatomy/UNC01_pos_pruned001_pos.nii.gz')
gl.colorname(1,"8redyell")
gl.minmax(1, 0.9, 2)

# UNC 0.01 NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_late/reliable_anatomy/UNC01_pos_pruned001_neg.nii.gz')
gl.colorname(2,"electric_blue")
gl.minmax(2, 0.8, 2)

# UNC 0.001 POSITIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_late/reliable_anatomy/unc001_pos.nii.gz')
gl.colorname(3,"8redyell")
gl.minmax(3, 0, 1.8)

# UNC 0.001 NEGATIVE
gl.overlayload('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_late/reliable_anatomy/unc001_neg.nii.gz')
gl.colorname(4,"electric_blue")
gl.minmax(4, 0, 2.2)

gl.mosaic("A H 0.08 V 0.08 39 27 -5 S H 0.08 V 0.08 -35 20 51 C H 0.08 V 0.08 -29 -62")
#gl.meshangle(45, 30, 0)  # rota el render 0.08

#gl.savebmp('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/__FIGURES_ARTICLE/mosaic.png')

# H 0 V 0 39 27 -5 o -4
# S H 0 V 0 -35 20 51
# C H 0 V 0 -27 o -28 -62