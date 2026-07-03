#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 12:46:13 2025

@author: acalvet
"""
from os.path import join
import pandas as pd

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask'
savedir = join(basedir, '1_sig_evaluation')

data = pd.read_excel(join(savedir, 'pat_exp_all_signatures.xlsx'), index_col=0)
dist_sample = pd.read_excel(join(basedir, '2_SVM_results_stai', 'train_test_sample_set.xlsx'))
tr_set = list(dist_sample.TRAIN_SET.dropna())
ts_set = list(dist_sample.TEST_SET.dropna())

vits_cond_accuracy = [0.91, 0.97]
results_accuracy = pd.DataFrame(columns=['COND_TR', 'REV_TR', 'COND_TS', 'REV_TS'])

for i in range(int(len(data.columns)/4)):
    sig_name = data.columns[i*4][:-4]
    
    results_accuracy.loc[sig_name, 'COND_TR'] = sum(data.loc[tr_set, sig_name + '_CSp'] > data.loc[tr_set, sig_name + '_CSm'])/len(tr_set)
    results_accuracy.loc[sig_name, 'REV_TR'] = sum(data.loc[tr_set, sig_name + '_CSprev'] > data.loc[tr_set, sig_name + '_CSmrev'])/len(tr_set)
    
    results_accuracy.loc[sig_name, 'COND_TS'] = sum(data.loc[ts_set, sig_name + '_CSp'] > data.loc[ts_set, sig_name + '_CSm'])/len(ts_set)
    results_accuracy.loc[sig_name, 'REV_TS'] = sum(data.loc[ts_set, sig_name + '_CSprev'] > data.loc[ts_set, sig_name + '_CSmrev'])/len(ts_set)
    

