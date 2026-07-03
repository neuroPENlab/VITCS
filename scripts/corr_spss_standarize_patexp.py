#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 12:16:28 2024

@author: acalvet
"""
from os.path import join
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

path = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/4_correlations_spss/SEPARADES_X_SIG/regressions_with_vifs'

patexp = pd.read_excel(join(path, 'pat_exp_var_vifs.xlsx'), index_col=0)
patexp_scaled = patexp

col_our = np.where(patexp.columns.str.contains('Our_sig'))[0]
col_threat = np.where(patexp.columns.str.contains('Threat'))[0]
col_suitas = np.where(patexp.columns.str.contains('SUITAS'))[0]
col_vifs = np.where(patexp.columns.str.contains('VIFS'))[0]

scaler = StandardScaler()

for col in [col_our, col_threat, col_suitas, col_vifs]:
    patexp_scaled.iloc[:, col] = scaler.fit_transform(patexp.iloc[:, col].values.reshape(-1,1)).reshape(patexp.iloc[:, col].shape)


patexp_scaled.to_excel(join(path, 'pat_exp_var_vifs_scaled.xlsx'))
