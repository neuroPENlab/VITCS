#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 14:27:08 2024

@author: acalvet

Multivariate Logistic Regression
"""
from os.path import join
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask'
savedir = join(basedir,'Mult_log_regression', 'excels_same_subj')

path_exc = join(basedir, '3_sig_evaluation_test', 'results_new_CS+CS-diff') #all_sig_patexp
path_subj_used = join(basedir, 'SVM_anxiety')
path_var = join(basedir, 'cluster_analysis')
subj = pd.read_excel(join(path_subj_used, 'subject_inclusion.xlsx'), index_col=0)
patexp = pd.read_excel(join(path_exc, 'all_pat_exp_new.xlsx'), index_col=0)
var = pd.read_excel(join(path_var, 'MVPA_dataset_pca.xlsx'), index_col=0).add_prefix("sub-", axis=0)

patexp.columns = patexp.columns.str.replace('Our_sig', 'VITS')
patexp_used = patexp.filter(like="VITS")

patexp_subj = subj.merge(patexp_used, left_index=True, right_index=True)

questionnaires = ['IQ_STAI_T_A', 'IQ_EMA_2weeks_first', 'IQ_SCSR_P_A', 'IQ_DASS_A_pre', 'IQ_DASS_S_pre', 'IQ_DASS_D_pre']

for q in questionnaires:
    patexp_subj_used = patexp_subj.loc[:, [q] + list(patexp_used.columns.values)]
    patexp_subj_used = patexp_subj_used[patexp_subj_used[q]!=0]
    patexp_subj_used = patexp_subj_used.merge(var[['Age','Sex',q[3:]]], left_index=True, right_index=True)
    patexp_subj_used.Sex = patexp_subj_used.Sex.map({'Man': 0, 'Woman': 1})
    
    # Count -1 and 1
    if sum(patexp_subj_used[q] == 1) > sum(patexp_subj_used[q] == -1):
        size_del = sum(patexp_subj_used[q] == 1) - sum(patexp_subj_used[q] == -1)
        subj_del = np.where(patexp_subj_used[q[3:]] == patexp_subj_used[patexp_subj_used[q] == 1][q[3:]].min())[0]
        rand_num = np.random.choice(subj_del, size=size_del, replace=False)
        if size_del > 1:
            patexp_subj_used = patexp_subj_used.drop(index=patexp_subj_used.iloc[rand_num].index)
        else:
            patexp_subj_used = patexp_subj_used.drop(index=patexp_subj_used.iloc[rand_num[0]].name)
        
    elif sum(patexp_subj_used[q] == 1) < sum(patexp_subj_used[q] == -1):
        size_del = sum(patexp_subj_used[q] == -1) - sum(patexp_subj_used[q] == 1)
        subj_del = np.where(patexp_subj_used[q[3:]] == patexp_subj_used[patexp_subj_used[q] == -1][q[3:]].max())[0]
        rand_num = np.random.choice(subj_del, size=size_del, replace=False)
        if size_del > 1:
            patexp_subj_used = patexp_subj_used.drop(index=patexp_subj_used.iloc[rand_num].index)
        else:
            patexp_subj_used = patexp_subj_used.drop(index=patexp_subj_used.iloc[rand_num[0]].name)
    
    patexp_subj_used[q][patexp_subj_used[q]==-1] = 0 # Canviar -1 per 0
    
    patexp_subj_used.to_excel(join(savedir, q + '.xlsx'))

for q in questionnaires:
    patexp_subj_used = patexp_subj.loc[:, [q] + list(patexp_used.columns.values)]
    patexp_subj_used = patexp_subj_used.merge(var[['Age','Sex',q[3:]]], left_index=True, right_index=True)
    patexp_subj_used.Sex = patexp_subj_used.Sex.map({'Man': 0, 'Woman': 1})
    patexp_subj_used.to_excel(join(savedir, q + '_all_sample.xlsx'))


pc1_excel = pd.read_excel(join(basedir, 'CCA', 'pc1_data.xlsx'), index_col=0)
pc1_excel_all = pd.read_excel(join(basedir, 'CCA', 'pc1_all_data.xlsx'), index_col=0).add_prefix('sub-', axis=0)

patexp_subj = pc1_excel_all.merge(patexp_used, left_index=True, right_index=True).merge(var[['Age','Sex']], left_index=True, right_index=True)
patexp_subj.to_excel(join(savedir, 'pc1_all_data.xlsx'))







plt.hist([patexp_subj_used[patexp_subj_used.Sex == 'Man'].SCSR_P_A, patexp_subj_used[patexp_subj_used.Sex == 'Woman'].SCSR_P_A], bins = 30, 
         color=['blue', 'green'], label=['Male', 'Female'], alpha=0.5)
plt.legend()
plt.xlabel('SCSR - P')
plt.ylabel('Count')


colors = {'Man': 'blue', 'Woman': 'green'}
markers = {1: 'o', -1: 'x'}  # 'o' per IQ=1, 'x' per IQ=-1

plt.figure(figsize=(10, 6))

for sex in patexp_subj_used['Sex'].unique():
    for iq in patexp_subj_used['IQ_SCSR_P_A'].unique():
        subset = patexp_subj_used[(patexp_subj_used['Sex'] == sex) & (patexp_subj_used['IQ_SCSR_P_A'] == iq)]
        plt.scatter(
            subset['Age'], 
            subset['SCSR_P_A'], 
            c=colors[sex], 
            marker=markers[iq], 
            label=f"{sex}, IQ={iq}", 
            alpha=0.7
        )

# Afegim detalls al gràfic
plt.xlabel('Age')
plt.ylabel('SCSR - P')
plt.title('Scatter plot: SCSR-P vs Age by Sex')
plt.legend()
plt.tight_layout()
plt.show()
