#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 15:22:56 2025

@author: acalvet

Multiple comparison correction
"""
import pandas as pd
from os.path import join
import statsmodels.stats.multitest as smm

#%% Linear Regression Model
basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/Mult_log_regression/PATTERN_EXPRESSION_late/feature_selection_method'
model_info = pd.read_excel(join(basedir, '_final_models_info_tertil.xlsx'), index_col=0)

pca1 = ['DASS_A', 'DASS_S', 'DASS_D', 'SCSR_P', 'STAI_T']
pca_all = ['DASS_A', 'DASS_S', 'DASS_D', 'SCSR_P', 'STAI_T', 'ASI', 'IoUS', 'LSAS', 'PSWQ', 'TAG']

pval_pca1 = model_info.loc[pca1, 'f_pval'].dropna()
pval_all = model_info.loc[pca_all, 'f_pval'].dropna()

# Bonferroni
rej_bonf_pca1, pvals_bonf_pca1, _, _ = smm.multipletests(pval_pca1, alpha=0.05, method='bonferroni')
rej_bonf_all, pvals_bonf_all, _, _ = smm.multipletests(pval_all, alpha=0.05, method='bonferroni')

# FDR (Benjamini-Hochberg)
rej_fdr_pca1, pvals_fdr_pca1, _, _ = smm.multipletests(pval_pca1, alpha=0.05, method='fdr_bh')
rej_fdr_all, pvals_fdr_all, _, _ = smm.multipletests(pval_all, alpha=0.05, method='fdr_bh')

print("\nBonferroni (PCA1):", pvals_bonf_pca1, rej_bonf_pca1)
print("FDR (PCA1):", pvals_fdr_pca1, rej_fdr_pca1)

print("\nBonferroni (all):", pvals_bonf_all, rej_bonf_all)
print("FDR (all):", pvals_fdr_all, rej_fdr_all)


df_pca1 = pd.DataFrame({'pca1_BF': pvals_bonf_pca1, 'pca1_FDR': pvals_fdr_pca1}, index=pval_pca1.index)
df_all = pd.DataFrame({'all_BF': pvals_bonf_all, 'all_FDR': pvals_fdr_all}, index=pval_all.index)
model_info[['pca1_BF', 'pca1_FDR']] = df_pca1
model_info[['all_BF', 'all_FDR']] = df_all

model_info.to_excel(join(basedir, '_final_models_info_tertil_corrected.xlsx'))

#%% SVM
basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/SVM_anxiety_patexp_late/feature_selection'
model_info = pd.read_excel(join(basedir, 'ROC_all.xlsx'), index_col=0)

pca1 = ['DASS_A', 'DASS_S', 'DASS_D', 'SCSR_P', 'STAI_T']

pval_pca1 = model_info.loc[pca1, 'P'].dropna()

# Bonferroni
rej_bonf_pca1, pvals_bonf_pca1, _, _ = smm.multipletests(pval_pca1, alpha=0.05, method='bonferroni')

# FDR (Benjamini-Hochberg)
rej_fdr_pca1, pvals_fdr_pca1, _, _ = smm.multipletests(pval_pca1, alpha=0.05, method='fdr_bh')

print("\nBonferroni (PCA1):", pvals_bonf_pca1, rej_bonf_pca1)
print("FDR (PCA1):", pvals_fdr_pca1, rej_fdr_pca1)

df_pca1 = pd.DataFrame({'pca1_BF': pvals_bonf_pca1, 'pca1_FDR': pvals_fdr_pca1}, index=pval_pca1.index)
model_info[['pca1_BF', 'pca1_FDR']] = df_pca1

model_info.to_excel(join(basedir, 'ROC_all_corrected.xlsx'))









