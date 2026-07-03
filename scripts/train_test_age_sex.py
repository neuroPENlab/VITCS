#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 11:19:41 2025

@author: acalvet

Check TRAIN - TEST sets AGE and SEX differences
"""

from os.path import join
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, chi2_contingency

subbase = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git'
basedir = join(subbase, 'results', 'final_brainmask')

train_test = pd.read_excel(join(basedir, '2_SVM_results_stai_sex', 'train_test_sample_set.xlsx'))
var = pd.read_excel(join(subbase, 'FIS_AX_per_Angels_27_06_25_puntuacions_totals.xlsx'), index_col=0).add_prefix("sub-", axis=0)

train_set = list(train_test.TRAIN_SET)
test_set = list(train_test.TEST_SET.dropna())

## AGE
var.loc[train_set, 'Age_A'].describe()
var.loc[test_set, 'Age_A'].describe()

t_stat, p_val = ttest_ind(var.loc[train_set, 'Age_A'], var.loc[test_set, 'Age_A'], equal_var=False)
print(f"\nT-test between age: T = {t_stat:.2f}, p = {p_val:.4f}")

## SEX
train_sex_counts = var.loc[train_set, 'Sex'].value_counts().sort_index()
test_sex_counts = var.loc[test_set, 'Sex'].value_counts().sort_index()

contingency = np.array([
    [train_sex_counts.get(0, 0), train_sex_counts.get(1, 0)],
    [test_sex_counts.get(0, 0), test_sex_counts.get(1, 0)]
])
chi2, p_chi, _, _ = chi2_contingency(contingency)
print(f"\nChi-quadrat per sex: χ² = {chi2:.2f}, p = {p_chi:.4f}")

##  PROBLEMA! 0.04