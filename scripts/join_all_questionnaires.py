#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 17:50:20 2024

@author: acalvet
"""
from os.path import join
import pandas as pd
import os

basedir = '/Users/acalvet/Documents/MVPA_FISAX'

dataset = pd.read_excel(join(basedir, 'MVPA_dataset_new.xlsx'), index_col=2)
dataset = dataset.drop(dataset.columns[[0, 1]], axis=1)
new_data = pd.read_excel(join(basedir, 'all_questionnaires_22.11.24.xlsx'), index_col=0)
ema_new = pd.read_excel(join(basedir, 'EMA_data_Marina_22.11.24.xlsx'), index_col=1)

search_for1 = ['Age_A', 'Sex', 'DASS_S_A', 'DASS_S_B', 'DASS_A_A', 'DASS_A_B', 'DASS_D_A', 'DASS_D_B', 
               'STAI_T_A', 'STAI_T_B', 'SCSR_P_A', 'SCSR_P_B', '', '']
search_for2 = ['Age', 'Sex', '', '', '', '', '', '', '', '', '', '', 'mean2Wfirst', 'mean2Wlast']
columns_list = ['Age', 'Sex', 'DASS_S_A', 'DASS_S_B', 'DASS_A_A', 'DASS_A_B', 'DASS_D_A', 'DASS_D_B', 
                'STAI_T_A', 'STAI_T_B', 'SCSR_P_A', 'SCSR_P_B', 'EMA_2weeks_first', 'EMA_2weeks_last']

# Check everything is correct
for col in range(len(columns_list)-1):
    if col == 0:
        check_correct = dataset[columns_list[col]].to_frame().merge(new_data[search_for1[col]], left_index=True, right_index=True).merge(
            ema_new[search_for2[col]], left_index=True, right_index=True)
        if not check_correct.iloc[:,0].equals(check_correct.iloc[:,1]) or not check_correct.iloc[:,0].equals(check_correct.iloc[:,2]):
            print('Mismatch in ' + columns_list[col])
    elif col == 1:
        check_correct = dataset[columns_list[col]].replace({'Man': 0, 'Woman': 1}).to_frame().merge(new_data[search_for1[col]], left_index=True, right_index=True).merge(
            ema_new[search_for2[col]].replace({'Man': 0, 'Woman': 1}), left_index=True, right_index=True)
        if not check_correct.iloc[:,0].equals(check_correct.iloc[:,1]) or not check_correct.iloc[:,0].equals(check_correct.iloc[:,2]):
            print('Mismatch in ' + columns_list[col])
    else:
        if search_for1[col] != '':
            check_correct = dataset[columns_list[col]].to_frame().merge(new_data[search_for1[col]], left_index=True, right_index=True)
            check_correct = check_correct.dropna()
            if not (check_correct.iloc[:,0] == check_correct.iloc[:,1]).all():
                print('Mismatch in ' + columns_list[col])
        elif search_for2[col] != '':
            check_correct = dataset[columns_list[col]].to_frame().merge(ema_new[search_for2[col]], left_index=True, right_index=True)
            check_correct = check_correct.dropna()
            if not (check_correct.iloc[:,0] == check_correct.iloc[:,1]).all():
                print('Mismatch in ' + columns_list[col])


# Build new dataset with only necessary information
list_mri = sorted(os.listdir(join(basedir, 'TFM_git', 'contrasts_brainmask')))[1:]
list_mri = list(map(lambda x: x.replace( 'sub-', ''), map(str, list_mri)))
new_dataset = pd.DataFrame(index=list_mri)

for col in range(len(columns_list)):
    if search_for1[col] != '':
        new_dataset = new_dataset.merge(new_data[search_for1[col]], left_index=True, right_index=True, how='left')
    elif search_for2[col] != '':
        new_dataset = new_dataset.merge(ema_new[search_for2[col]], left_index=True, right_index=True, how='left')

new_dataset.columns = columns_list
new_dataset.to_excel(join(basedir, 'Quest_final_dataset.xlsx'))
