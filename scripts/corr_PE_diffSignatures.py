#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 11:53:07 2025

@author: acalvet

Calculate correlation between PE expression across subjects and different signatures
"""
from os.path import join
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask'
patexp = pd.read_excel(join(basedir, '3_sig_evaluation_test', 'results_new_CS+CS-diff', 'all_pat_exp_new.xlsx'), index_col=0)

pe_type = ['CS+', 'CS-', 'CS+early', 'CS+late', 'CS-early', 'CS-late', 'CS+rev', 'CS-rev', 'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate']
sig = ['VITS', 'Threat', 'SUITAS']

res_c = pd.DataFrame(columns=pe_type)
res_p = pd.DataFrame(columns=pe_type)

for pe in pe_type:
    # VITS vs Threat
    res_c.loc[sig[0] + 'vs' + sig[1], pe] = pearsonr(patexp[sig[0] + '_' + pe], patexp[sig[1] + '_' + pe]).statistic
    res_p.loc[sig[0] + 'vs' + sig[1], pe] = pearsonr(patexp[sig[0] + '_' + pe], patexp[sig[1] + '_' + pe]).pvalue
    # VITS vs SUITAS
    res_c.loc[sig[0] + 'vs' + sig[2], pe] = pearsonr(patexp[sig[0] + '_' + pe], patexp[sig[2] + '_' + pe]).statistic
    res_p.loc[sig[0] + 'vs' + sig[2], pe] = pearsonr(patexp[sig[0] + '_' + pe], patexp[sig[2] + '_' + pe]).pvalue
    # Threat vs SUITAS
    res_c.loc[sig[1] + 'vs' + sig[2], pe] = pearsonr(patexp[sig[1] + '_' + pe], patexp[sig[2] + '_' + pe]).statistic
    res_p.loc[sig[1] + 'vs' + sig[2], pe] = pearsonr(patexp[sig[1] + '_' + pe], patexp[sig[2] + '_' + pe]).pvalue

res_c = res_c.astype(float)
res_p = res_p.astype(float)

vmax = 0.054
bounds = np.linspace(0, vmax, 256)
cmap = plt.cm.YlOrBr
new_colors = cmap(np.linspace(0, 1, 256))
new_colors[-1] = [0, 0, 0, 1]  # RGBA para negro
custom_cmap = mcolors.ListedColormap(new_colors)
norm = mcolors.BoundaryNorm(bounds, custom_cmap.N)

fig, axs = plt.subplots(2, 1, figsize=(30,20))  # Creates a 2x2 grid of subplots with a size of 10x10 inches
sns.set(font_scale=2)
sns.heatmap(res_c, ax=axs[0], cmap='coolwarm')
axs[0].set_title('Correlation coefficient', fontsize=35)
axs[0].tick_params(axis='both', labelsize=22)
axs[0].set_xticklabels(axs[0].get_xticklabels(), rotation=30, ha='right')
sns.heatmap(res_p, ax=axs[1], cmap=custom_cmap, norm=norm)
axs[1].set_title('p-value', fontsize=35)
axs[1].tick_params(axis='both', labelsize=22)
axs[1].set_xticklabels(axs[1].get_xticklabels(), rotation=30, ha='right')