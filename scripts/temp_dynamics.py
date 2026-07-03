#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:21:47 2026

@author: acalvet
"""
import pandas as pd
from os.path import join
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai'

pat_exp = pd.read_excel(join(basedir, 'pat_exp_all_data_xval.xlsx'))

pat_exp_long = pat_exp.melt(id_vars='Row', value_vars=['CS+early', 'CS+late', 'CS+revearly', 'CS+revlate','CS-early', 'CS-late', 'CS-revearly', 'CS-revlate'], 
                            var_name='condition', value_name='value')

pat_exp_long[['CS', 'phase']] = pat_exp_long['condition'].str.extract(r'(CS[+-])(.*)')

# Media por sujeto
subj_mean = pat_exp_long.groupby('Row')['value'].transform('mean')
# Media global
grand_mean = pat_exp_long['value'].mean()
# Normalización
pat_exp_long['value_norm'] = pat_exp_long['value'] - subj_mean + grand_mean

# Número de condiciones
n_cond = pat_exp_long['condition'].nunique()
# Agrupar
summary = pat_exp_long.groupby(['CS', 'phase']).agg(mean=('value', 'mean'), std_norm=('value_norm', 'std'),
                                                    n=('Row', 'count')).reset_index()
# Error estándar con corrección Morey
summary['sem'] = summary['std_norm'] / np.sqrt(summary['n']) * np.sqrt(n_cond / (n_cond - 1))



plt.figure(figsize=(10,6))
sns.barplot(data=summary, x='phase', y='mean', hue='CS', capsize=.1, errwidth=1, ci=None)
for i, row in summary.iterrows():
    x_pos = i % 4 + (-0.2 if row['CS']=='CS+' else 0.2)
    plt.errorbar(x=x_pos, y=row['mean'], yerr=row['sem'], 
                 fmt='none', color='black', capsize=5)

sns.pointplot(data=pat_exp_long, x='phase', y='value', hue='CS', dodge=0.4, join=True, markers='o', ci=None, alpha=0.4)
plt.legend(title='CS')
plt.title('Barplot with within-subject error')
plt.show()


phase_order = ['early', 'late', 'revearly', 'revlate']
# --- FIGURA ---
fig, axes = plt.subplots(1, 2, figsize=(12,5), sharey=True)
palette = {
    'CS+': ['#4C72B0']*4,   # azul
    'CS-': ['#DD8452']*4    # naranja
}

for ax, cs in zip(axes, ['CS+','CS-']):
    data_sum = summary[summary['CS'] == cs]
    data_raw = pat_exp_long[pat_exp_long['CS'] == cs]
    sns.barplot(data=data_sum, x='phase', y='mean', ax=ax, color=palette[cs][0], ci=None)
    for i, row in data_sum.iterrows():
        ax.errorbar(x=phase_order.index(row['phase']), y=row['mean'], yerr=row['sem'], color='black', capsize=4, fmt='none')

    sns.lineplot(data=data_raw, x='phase', y='value', units='Row', estimator=None, color='gray', alpha=0.2, lw=1, ax=ax)
    sns.scatterplot(data=data_raw, x='phase', y='value', color='gray', alpha=0.4, s=40, legend=False, ax=ax)
    ax.set_title(cs)
    ax.set_xlabel('')
axes[0].set_ylabel('Value')
axes[1].set_ylabel('')
plt.tight_layout()
plt.show()



