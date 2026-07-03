#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 09:27:11 2025

@author: acalvet
"""
from os.path import join
import nibabel as nib
import numpy as np
from skimage.morphology import binary_opening, binary_dilation, ball

path='/Users/acalvet/Documents/MVPA_FISAX/DATA/neurosynth_masks'

img_info = nib.load(join(path, 'neurosynth_mask.nii.gz'))
img = img_info.get_fdata().astype(bool)


footprint = np.zeros((3, 3, 3), dtype=bool)
footprint[1, 1, 1] = 1
footprint[1, 1, 2] = 1

opened = binary_opening(img, footprint=footprint)

dilated = binary_dilation(opened, footprint=ball(2))

img_opended_dil = nib.Nifti1Image(dilated.astype(np.uint8), affine=img_info.affine, header=img_info.header)
nib.save(img_opended_dil, join(path, 'neurosynth_mask_open2_dil2.nii.gz'))