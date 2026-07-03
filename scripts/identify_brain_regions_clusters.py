#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 12:36:58 2025

@author: acalvet
"""
import nibabel as nib
from scipy.ndimage import label
import numpy as np
import pandas as pd

atlas_path = '/Users/acalvet/Documents/MVPA_FISAX/DATA/HarvardOxford-cort-maxprob-thr25-2mm_resampled.nii.gz'
# atlas_path = '/Users/acalvet/Documents/MVPA_FISAX/DATA/AAL3v1_resampled.nii.gz'
# HarvardOxford-cort-maxprob-thr0-2mm_resampled.nii.gz / HarvardOxford-cort-maxprob-thr25-2mm_resampled.nii.gz
# HarvardOxford-sub-maxprob-thr0-2mm_resampled.nii.gz / HarvardOxford-sub-maxprob-thr25-2mm_resampled.nii.gz
clusters_path = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/fdr05_pos.nii.gz'
weights_path = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/svm_results_unthresholded.nii'

excel_regions = pd.DataFrame(columns=['cluster', 'N_voxels', 'cl_mean', 'peak_coord', 'peak_value', 'peak_region', 'region_N', 'n_voxels'])

# Load atlas and cluster images (they have to be in the same space!)
atlas_img = nib.load(atlas_path)
atlas = atlas_img.get_fdata()
clusters = nib.load(clusters_path).get_fdata()
weights = nib.load(weights_path).get_fdata()

# Etiqueta components connexos
labeled_clusters, n_clusters = label(clusters > 0)
print(f"There are {n_clusters} independent clusters")

for cid in range(1, n_clusters + 1):
    mask = (labeled_clusters == cid)
    atlas_in_cluster = atlas * mask
    weights_in_cluster = weights * mask
    
    coords = np.argwhere(mask)  # voxels del clúster
    values = weights[mask]     # valors del weight
    peak_idx = np.argmax(np.abs(values))
    peak_coord = coords[peak_idx]
    mni_peak_coord = nib.affines.apply_affine(atlas_img.affine, peak_coord)
    peak_value = values[peak_idx]
    weight_mean = np.mean(values)
    atlas_value_at_peak = atlas[tuple(peak_coord)]
    print(f"Peak del clúster: coord={mni_peak_coord}, weight={peak_value}, atlas_region={atlas_value_at_peak}")
    
    regions = np.unique(atlas_in_cluster[atlas_in_cluster > 0])
    print(f"Cluster {cid} solapa amb {len(regions)} regions de l’atles: {regions}")
    
    if len(regions) > 0:
        for reg in regions:
            excel_regions.loc[len(excel_regions)] = [cid, sum(sum(sum(mask>0))), weight_mean, mni_peak_coord, peak_value, 
                                                     atlas_value_at_peak, reg, sum(sum(sum(atlas_in_cluster==reg)))]
    else:
        excel_regions.loc[len(excel_regions)] = [cid, sum(sum(sum(mask>0))), weight_mean, mni_peak_coord, peak_value, 
                                                 atlas_value_at_peak, np.nan, np.nan]

excel_regions.to_excel('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_early/reliable_anatomy/AAL3_fdr05_positive.xlsx')
