#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: acalvet
"""
import pandas as pd
from wordcloud import WordCloud

# Create WordCloud object
wc = WordCloud(
    background_color='white',
    width=800,
    height=150,
    margin=2,
    prefer_horizontal=1,
    relative_scaling=0.6,
    colormap='viridis'
)
# Define text based on Neurosynth terms from the decoding
save_path = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai'
path_excel = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/neurosynth_unc001_pruned05.xlsx'
excel = pd.read_excel(path_excel, sheet_name='NEGATIVE_ABS') # ALL POSITIVE NEGATIVE_ABS NEGATIVE

# Generate the word cloud ANATOMIC from the text data
text_anat = excel.loc[:,['Anatomic','Correlation_S']].set_index('Anatomic').to_dict()['Correlation_S']
wc.fit_words(text_anat)
# Save the word cloud to an image file
wc.to_file(save_path + '/neurosynth_WC_anatomic_NEG_ABS.png')

# Generate the word cloud FUNCTIONAL from the text data
text_func = excel.loc[:,['Functional','Correlation_F']].set_index('Functional').to_dict()['Correlation_F']
wc.fit_words(text_func)
# Save the word cloud to an image file
wc.to_file(save_path + '/neurosynth_WC_functional_NEG_ABS.png')



### PASSAR A Z-SCORE!

# import nibabel as nib
# import scipy
# in_file = "./2_SVM_results_stai/svm_results_unthresholded.nii"
# msk_file = "./brainmask_canlab_bin_resampled.nii"
# data = nib.load(in_file)
# mat = data.get_fdata()
# msk = nib.load(msk_file)
# msk_img = msk.get_fdata()
# mat[msk_img == 1] = scipy.stats.zscore(mat[msk_img == 1])

# nib.save(nib.Nifti1Image(mat, data.affine), "./2_SVM_results_stai/svm_results_unthresholded_zscore.nii")