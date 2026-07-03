#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 13:00:02 2025

@author: acalvet

Calcular si existeix diferencia significativa entre els resultats de 2 models de SVM parellats
"""
from os.path import join
import pandas as pd
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.multitest import fdrcorrection

### EARLY - LATE
a = 101  # both correct
b = 13   # early correct, late incorrect
c = 19   # early incorrect, late correct
d = 5    # both incorrect

table_early_late = np.array([[a, b], [c, d]])

### ALL - EARLY
a = 109  # both correct
b = 16   # all correct, early incorrect
c = 5   # all incorrect, early correct
d = 8    # both incorrect

table_all_early = np.array([[a, b], [c, d]])

### ALL - LATE
a = 113  # both correct
b = 12   # all correct, late incorrect
c = 7   # all incorrect, late correct
d = 6    # both incorrect

table_all_late = np.array([[a, b], [c, d]])

# Test de McNemar (exacto binomial o chi2 con corrección de continuidad)
print('EARLY vs LATE')
result_early_late = mcnemar(table_early_late, exact=False, correction=True)   # exact=True usa binomial exacto
print(f"statistic={result_early_late.statistic}, p-value={result_early_late.pvalue}")

print('ALL vs EARLY')
result_all_early = mcnemar(table_all_early, exact=False, correction=True)   # exact=True usa binomial exacto
print(f"statistic={result_all_early.statistic}, p-value={result_all_early.pvalue}")

print('ALL vs LATE')
result_all_late = mcnemar(table_all_late, exact=False, correction=True)   # exact=True usa binomial exacto
print(f"statistic={result_all_late.statistic}, p-value={result_all_late.pvalue}")

# Millor forma
path = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask'

tr_ts = pd.read_excel(join(path, '2_SVM_results_stai', 'train_test_sample_set.xlsx'))
pe_all = pd.read_excel(join(path, '2_SVM_results_stai', 'pat_exp_all_data_xval_10fold.xlsx'), index_col=0)
pe_early = pd.read_excel(join(path, '2_SVM_results_stai_early', 'pat_exp_early_all_data_xval_10fold.xlsx'), index_col=0)
pe_late = pd.read_excel(join(path, '2_SVM_results_stai_late', 'pat_exp_late_all_data_xval_10fold.xlsx'), index_col=0)

FC_all = pe_all.loc[tr_ts.TRAIN_SET, 'CS+'] > pe_all.loc[tr_ts.TRAIN_SET, 'CS-']
FC_early = pe_early.loc[tr_ts.TRAIN_SET, 'CS+early'] > pe_early.loc[tr_ts.TRAIN_SET, 'CS-early']
FC_late = pe_late.loc[tr_ts.TRAIN_SET, 'CS+late'] > pe_late.loc[tr_ts.TRAIN_SET, 'CS-late']

# VITCS vs VITCS-early 
a = sum(np.logical_and(FC_all, FC_early)) # both correct
b = sum(np.logical_and(FC_all, FC_early == 0)) # 1st correct, 2nd incorrect
c = sum(np.logical_and(FC_all == 0, FC_early)) # 1st incorrect, 2nd correct
d = sum(np.logical_and(FC_all == 0, FC_early == 0)) # both incorrect
mcnemar(np.array([[a, b], [c, d]]), exact=True, correction=False).statistic
mcnemar(np.array([[a, b], [c, d]]), exact=True, correction=False).pvalue

# VITCS vs VITCS-late 
a = sum(np.logical_and(FC_all, FC_late)) # both correct
b = sum(np.logical_and(FC_all, FC_late == 0)) # 1st correct, 2nd incorrect
c = sum(np.logical_and(FC_all == 0, FC_late)) # 1st incorrect, 2nd correct
d = sum(np.logical_and(FC_all == 0, FC_late == 0)) # both incorrect
mcnemar(np.array([[a, b], [c, d]]), exact=True, correction=False).statistic
mcnemar(np.array([[a, b], [c, d]]), exact=True, correction=False).pvalue

# VITCS-early vs VITCS-late 
a = sum(np.logical_and(FC_early, FC_late)) # both correct
b = sum(np.logical_and(FC_early, FC_late == 0)) # 1st correct, 2nd incorrect
c = sum(np.logical_and(FC_early == 0, FC_late)) # 1st incorrect, 2nd correct
d = sum(np.logical_and(FC_early == 0, FC_late == 0)) # both incorrect
mcnemar(np.array([[a, b], [c, d]]), exact=False, correction=False).statistic
mcnemar(np.array([[a, b], [c, d]]), exact=False, correction=False).pvalue

#### FROM OTHER SIGNATURES
path = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/1_sig_evaluation'

FC = pd.read_excel(join(path, 'FC_signatures_all.xlsx'), index_col=0)

# check_sig = ['VITCS-Reddan', 'VITCS-SUITAS', 'VITCS-Zhou', 'VITCS-Wen', 'VITCS-NPS', 'VITCS-Ceko_general',
#              'VITCS-Ceko_mechanical', 'VITCS-Ceko_thermal', 'VITCS-Ceko_sound', 'VITCS-Ceko_visual', 'VITCS-craving', 
#              'Reddan-SUITAS', 'Reddan-NPS', 'SUITAS-Zhou', 'Zhou-Wen']

check_sig = ['VITCS-Reddan', 'Reddan-SUITAS', 'Reddan-Zhou', 'Reddan-NPS', 'Reddan-Ceko_general',
             'SUITAS-Zhou', 'SUITAS-Wen', 'SUITAS-Ceko_general', 'Zhou-Wen']

results = pd.DataFrame(index = check_sig, columns = ['statistic', 'pvalue'])
for sigs in check_sig:
    a = sum(np.logical_and(FC.loc[:, sigs.split('-')[0]], FC.loc[:, sigs.split('-')[1]])) # both correct
    b = sum(np.logical_and(FC.loc[:, sigs.split('-')[0]], FC.loc[:, sigs.split('-')[1]] == 0)) # 1st correct, 2nd incorrect
    c = sum(np.logical_and(FC.loc[:, sigs.split('-')[0]] == 0, FC.loc[:, sigs.split('-')[1]])) # 1st incorrect, 2nd correct
    d = sum(np.logical_and(FC.loc[:, sigs.split('-')[0]] == 0, FC.loc[:, sigs.split('-')[1]] == 0)) # both incorrect
 
    if b + c < 25:
        print('yes')
        
    results.loc[sigs, 'statistic'] = mcnemar(np.array([[a, b], [c, d]]), exact=False, correction=False).statistic
    results.loc[sigs, 'pvalue'] = mcnemar(np.array([[a, b], [c, d]]), exact=False, correction=False).pvalue


results.loc[:, 'pvalue_adj'] = fdrcorrection(results.loc[:, 'pvalue'])[1]

results.to_excel(join(path, 'comparison_signatures_ts_chi.xlsx'))

#### FROM OTHER SIGNATURES - ENIGMA!
path = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/ENIGMA_FC/results_other_sig'
data = pd.read_excel(join(path, 'pattern_ENIGMA_vits_reddan_suitas.xlsx'), index_col=0)
datasets = np.array([2, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 22, 23, 24, 25, 26, 28, 30, 31, 32, 33, 36, 38, 39, 40, 41, 42, 43]) - 1
data = data[data.dataset.isin(data.dataset.unique()[datasets])]

check_sig = ['VITS-reddan', 'VITS-suitas', 'reddan-suitas']

results = pd.DataFrame(index = check_sig, columns = ['statistic', 'pvalue'])
for sigs in check_sig:
    a = sum(np.logical_and(data.loc[:, sigs.split('-')[0]]>0, data.loc[:, sigs.split('-')[1]]>0)) # both correct
    b = sum(np.logical_and(data.loc[:, sigs.split('-')[0]]>0, data.loc[:, sigs.split('-')[1]]<0)) # 1st correct, 2nd incorrect
    c = sum(np.logical_and(data.loc[:, sigs.split('-')[0]]<0, data.loc[:, sigs.split('-')[1]]>0)) # 1st incorrect, 2nd correct
    d = sum(np.logical_and(data.loc[:, sigs.split('-')[0]]<0, data.loc[:, sigs.split('-')[1]]<0)) # both incorrect
 
    if b + c < 25:
        print('yes')
        
    results.loc[sigs, 'statistic'] = mcnemar(np.array([[a, b], [c, d]]), exact=False, correction=False).statistic
    results.loc[sigs, 'pvalue'] = mcnemar(np.array([[a, b], [c, d]]), exact=False, correction=False).pvalue


results.loc[:, 'pvalue_adj'] = fdrcorrection(results.loc[:, 'pvalue'])[1]

results.to_excel(join(path, 'comparison_signatures_chi.xlsx'))







