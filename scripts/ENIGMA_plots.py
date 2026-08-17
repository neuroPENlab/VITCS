#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 14:05:39 2024

@author: acalvet

ENIGMA plots
"""
from os.path import join
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, sem
import numpy as np

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/ENIGMA_FC/results'
# data = pd.read_excel(join(basedir, 'path_info_subj_pattern_late.xlsx'), index_col=0)
data = pd.read_excel(join(basedir, 'pattern_ENIGMA_vits_early_late.xlsx'), index_col=0)
data_2groups = data.groupby('dataset').filter(lambda x: x['group'].nunique() == 2)
data_2sex = data.groupby('dataset').filter(lambda x: x['sex'].nunique() == 2)


QC_dataset = pd.DataFrame(index=data.dataset.unique(), columns=['dataset_num', 'N', 'T', 'kmax', 'age_m', 'age_sd', 
                                                                'age_min', 'age_max', 'sex_0', 'sex_1', 
                                                                'diagnosis', 'CS_type', 'US_type', 'pair_rate', 'acc'])
QC_dataset.dataset_num = range(1,len(data.dataset.unique())+1)
QC_dataset.N = [18, 41, 12, 10, 13, 14, 16, 9, 38, 61, 71, 35, 147, 116, 80, 28, 29, 59, 59, 47, 29, 31, 
                60, 95, 38, 37, 14, 140, 13, 31, 112, 45, 42, 29, 21, 50, 28, 71, 45, 50, 278, 55, 82]
QC_dataset.T = [8.13, 10.41, 8.13, 9.35, 8.57, 9.17, 6.32, 11.3, 10.86, 7.85, 5.42, 9.94, 8.19, 11.26, 
                7.86, 4.94, 7.56, 6.16, 5.64, 5.37, 8.15, 9.08, 6.47, 10.01, 5.73, 7.01, 5.76, 6.52, 6.83, 
                5.03, 7.75, 5.88, 5.30, 4.23, 10.2, 16.56, 6.66, 8.8, 14.08, 6.61, 24.84, 8.81, 13.82]
QC_dataset.kmax = [584, 5181, 26, 46, 16, 475, 13, 18, 1928, 2088, 130, 44627, 4231, 36414, 
                   3134, 13, 526, 371, 235, 18, 120, 1027, 676, 59258, 178, 7262, 1, 2367, 72, 
                   123, 1262, 886, 67, 3, 3936, 3623, 138, 17563, 62483, 152, 71618, 35339, 68248]

for dset in QC_dataset.index:
    QC_dataset.loc[dset, 'age_m'] = data[data.dataset==dset].age.mean()
    QC_dataset.loc[dset, 'age_sd'] = data[data.dataset==dset].age.std()
    QC_dataset.loc[dset, 'age_min'] = data[data.dataset==dset].age.min()
    QC_dataset.loc[dset, 'age_max'] = data[data.dataset==dset].age.max()
    QC_dataset.loc[dset, 'sex_0'] = sum(data[data.dataset==dset].sex == 0)
    QC_dataset.loc[dset, 'sex_1'] = sum(data[data.dataset==dset].sex == 1)
    diag = ''
    for d in data[data.dataset==dset].diagnosis.unique():
        diag = diag + '_'  + d + '-' + str(sum(data[data.dataset==dset].diagnosis == d))
    QC_dataset.loc[dset, 'diagnosis'] = diag
    QC_dataset.loc[dset, 'CS_type'] = data[data.dataset==dset].CS_type.iloc[0]
    QC_dataset.loc[dset, 'US_type'] = data[data.dataset==dset].US_type.iloc[0]
    QC_dataset.loc[dset, 'pair_rate'] = data[data.dataset==dset].pair_rate.iloc[0]
    
QC_dataset_filt = QC_dataset[QC_dataset.N >= 15] # 20
QC_dataset_filt = QC_dataset_filt[QC_dataset_filt['T'] >= 6] # 5 o 5.5
QC_dataset_filt = QC_dataset_filt[QC_dataset_filt.kmax >= 20]

# Utilitzavem aquest
QC_dataset_filt1 = QC_dataset[QC_dataset.dataset_num.isin([1, 2, 9, 10, 12, 13, 14, 15, 22, 24,
                                                          26, 28, 31, 35, 36, 38, 39, 41, 42, 43])]

QC_dataset_filt2 = QC_dataset[QC_dataset.dataset_num.isin([2, 9, 12, 13, 14, 15, 22, 24,
                                                          35, 36, 38, 39, 41, 42, 43])]

# NEW
QC_dataset_filt3 = QC_dataset[QC_dataset.dataset_num.isin([2, 9, 10, 12, 13, 14, 15, 18, 19, 22, 23, 24, 25,
                                                          26, 28, 30, 31, 32, 33, 36, 38, 39, 40, 41, 42, 43])]

QC_dataset_filt3_old = QC_dataset[QC_dataset.dataset_num.isin([2, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 22, 23, 24, 25,
                                                          26, 28, 30, 31, 32, 33, 36, 38, 39, 40, 41, 42, 43])]
QC_dataset_filt3 = QC_dataset[QC_dataset.dataset_num.isin([2, 9, 10, 11, 12, 13, 14, 15, 18, 19, 22, 23, 24, 25,
                                                          26, 28, 30, 31, 32, 33, 36, 38, 39, 40, 41, 42, 43])]

QC_dataset_filt3 = QC_dataset[QC_dataset.dataset_num.isin([2, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 24, 25,
                                                          26, 28, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43])]

QC_dataset.N.sum()
QC_dataset_filt.N.sum()

data_filt1 = data[data.dataset.isin(QC_dataset_filt1.index)]
data_filt3 = data[data.dataset.isin(QC_dataset_filt3.index)]

for ds in np.unique(QC_dataset_filt3.index):
    QC_dataset_filt3.loc[ds, 'acc'] = (sum(data_filt3.loc[data_filt3.dataset == ds, 'VITS'] > 0))/len(data_filt3[data_filt3.dataset == ds])*100

QC_dataset_filt3.to_excel(join(basedir, 'ENIGMA_sample_description.xlsx'))


# per US
data_filt1_0 = data_filt1[data_filt1.US_type == 0]
data_filt1_1 = data_filt1[data_filt1.US_type == 1]

data_filt3_0 = data_filt3[data_filt3.US_type == 0]
data_filt3_1 = data_filt3[data_filt3.US_type == 1]
data_filt3_2 = data_filt3[np.isnan(data_filt3.US_type)]

# per rate
data_filt1_31 = data_filt1[data_filt1.pair_rate == 31]
data_filt1_33 = data_filt1[data_filt1.pair_rate == 33]
data_filt1_40 = data_filt1[data_filt1.pair_rate == 40]
data_filt1_50 = data_filt1[data_filt1.pair_rate == 50]
data_filt1_55 = data_filt1[data_filt1.pair_rate == 55]
data_filt1_625 = data_filt1[data_filt1.pair_rate == 62.5]
data_filt1_80 = data_filt1[data_filt1.pair_rate == 80]
data_filt1_100 = data_filt1[data_filt1.pair_rate == 100]

print('-------------- VITS --------------')
print('ALL DATA (20 datasets)')
print('N = ' + str(sum(data_filt1.VITS > 0)) + ' of ' + str(len(data_filt1)))
print('Accuracy = ' + str(sum(data_filt1.VITS > 0)/len(data_filt1) * 100))

print('ALL DATA (28 datasets N>30)')
print('N = ' + str(sum(data_filt3.VITS > 0)) + ' of ' + str(len(data_filt3)))
print('Accuracy = ' + str(sum(data_filt3.VITS > 0)/len(data_filt3) * 100))

print('-------------- REDDAN --------------')
print('ALL DATA')
print('N = ' + str(sum(data_filt1.reddan > 0)) + ' of ' + str(len(data_filt1)))
print('Accuracy = ' + str(sum(data_filt1.reddan > 0)/len(data_filt1) * 100))

print('ALL DATA (28 datasets N>30)')
print('N = ' + str(sum(data_filt3.reddan > 0)) + ' of ' + str(len(data_filt3)))
print('Accuracy = ' + str(sum(data_filt3.reddan > 0)/len(data_filt3) * 100))

print('-------------- SUITAS --------------')
print('ALL DATA')
print('N = ' + str(sum(data_filt1.suitas > 0)) + ' of ' + str(len(data_filt1)))
print('Accuracy = ' + str(sum(data_filt1.suitas > 0)/len(data_filt1) * 100))

print('ALL DATA (28 datasets N>30)')
print('N = ' + str(sum(data_filt3.suitas > 0)) + ' of ' + str(len(data_filt3)))
print('Accuracy = ' + str(sum(data_filt3.suitas > 0)/len(data_filt3) * 100))

print('-------------- VITS_early --------------')
print('ALL DATA (20 datasets)')
print('N = ' + str(sum(data_filt1.VITS_early > 0)) + ' of ' + str(len(data_filt1)))
print('Accuracy = ' + str(sum(data_filt1.VITS_early > 0)/len(data_filt1) * 100))

print('ALL DATA (28 datasets N>30)')
print('N = ' + str(sum(data_filt3.VITS_early > 0)) + ' of ' + str(len(data_filt3)))
print('Accuracy = ' + str(sum(data_filt3.VITS_early > 0)/len(data_filt3) * 100))

print('-------------- VITS_late --------------')
print('ALL DATA (20 datasets)')
print('N = ' + str(sum(data_filt1.VITS_late > 0)) + ' of ' + str(len(data_filt1)))
print('Accuracy = ' + str(sum(data_filt1.VITS_late > 0)/len(data_filt1) * 100))

print('ALL DATA (28 datasets N>30)')
print('N = ' + str(sum(data_filt3.VITS_late > 0)) + ' of ' + str(len(data_filt3)))
print('Accuracy = ' + str(sum(data_filt3.VITS_late > 0)/len(data_filt3) * 100))


print('-------------- VITS --------------')
print('US type = electric shock')
print('N = ' + str(sum(data_filt1_0.VITS > 0)) + ' of ' + str(len(data_filt1_0)))
print('Accuracy = ' + str(sum(data_filt1_0.VITS > 0)/len(data_filt1_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt1_1.VITS > 0)) + ' of ' + str(len(data_filt1_1)))
print('Accuracy = ' + str(sum(data_filt1_1.VITS > 0)/len(data_filt1_1) * 100))

print('-------------- REDDAN --------------')
print('US type = electric shock')
print('N = ' + str(sum(data_filt1_0.reddan > 0)) + ' of ' + str(len(data_filt1_0)))
print('Accuracy = ' + str(sum(data_filt1_0.reddan > 0)/len(data_filt1_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt1_1.reddan > 0)) + ' of ' + str(len(data_filt1_1)))
print('Accuracy = ' + str(sum(data_filt1_1.reddan > 0)/len(data_filt1_1) * 100))

print('-------------- SUITAS --------------')
print('US type = electric shock')
print('N = ' + str(sum(data_filt1_0.suitas > 0)) + ' of ' + str(len(data_filt1_0)))
print('Accuracy = ' + str(sum(data_filt1_0.suitas > 0)/len(data_filt1_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt1_1.suitas > 0)) + ' of ' + str(len(data_filt1_1)))
print('Accuracy = ' + str(sum(data_filt1_1.suitas > 0)/len(data_filt1_1) * 100))

### 30 datasets
print('-------------- VITS --------------')
print('US type = electric shock')
print('N = ' + str(sum(data_filt3_0.VITS > 0)) + ' of ' + str(len(data_filt3_0)))
print('Accuracy = ' + str(sum(data_filt3_0.VITS > 0)/len(data_filt3_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt3_1.VITS > 0)) + ' of ' + str(len(data_filt3_1)))
print('Accuracy = ' + str(sum(data_filt3_1.VITS > 0)/len(data_filt3_1) * 100))
print('US type = thermal stimulus')
print('N = ' + str(sum(data_filt3_2.VITS > 0)) + ' of ' + str(len(data_filt3_2)))
print('Accuracy = ' + str(sum(data_filt3_2.VITS > 0)/len(data_filt3_2) * 100))

print('-------------- REDDAN --------------')
print('US type = electric shock')
print('N = ' + str(sum(data_filt3_0.reddan > 0)) + ' of ' + str(len(data_filt3_0)))
print('Accuracy = ' + str(sum(data_filt3_0.reddan > 0)/len(data_filt3_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt3_1.reddan > 0)) + ' of ' + str(len(data_filt3_1)))
print('Accuracy = ' + str(sum(data_filt3_1.reddan > 0)/len(data_filt3_1) * 100))
print('US type = thermal stimulus')
print('N = ' + str(sum(data_filt3_2.reddan > 0)) + ' of ' + str(len(data_filt3_2)))
print('Accuracy = ' + str(sum(data_filt3_2.reddan > 0)/len(data_filt3_2) * 100))

print('-------------- SUITAS --------------')
print('US type = electric shock')
print('N = ' + str(sum(data_filt3_0.suitas > 0)) + ' of ' + str(len(data_filt3_0)))
print('Accuracy = ' + str(sum(data_filt3_0.suitas > 0)/len(data_filt3_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt3_1.suitas > 0)) + ' of ' + str(len(data_filt3_1)))
print('Accuracy = ' + str(sum(data_filt3_1.suitas > 0)/len(data_filt3_1) * 100))
print('US type = thermal stimulus')
print('N = ' + str(sum(data_filt3_2.suitas > 0)) + ' of ' + str(len(data_filt3_2)))
print('Accuracy = ' + str(sum(data_filt3_2.suitas > 0)/len(data_filt3_2) * 100))

print('-------------- VITS_early --------------')
print('US type = electric shock')
print('N = ' + str(sum(data_filt3_0.VITS_early > 0)) + ' of ' + str(len(data_filt3_0)))
print('Accuracy = ' + str(sum(data_filt3_0.VITS_early > 0)/len(data_filt3_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt3_1.VITS_early > 0)) + ' of ' + str(len(data_filt3_1)))
print('Accuracy = ' + str(sum(data_filt3_1.VITS_early > 0)/len(data_filt3_1) * 100))
print('US type = thermal stimulus')
print('N = ' + str(sum(data_filt3_2.VITS_early > 0)) + ' of ' + str(len(data_filt3_2)))
print('Accuracy = ' + str(sum(data_filt3_2.VITS_early > 0)/len(data_filt3_2) * 100))

print('-------------- VITS_late --------------')
print('US type = electric shock')
print('N = ' + str(sum(data_filt3_0.VITS_late > 0)) + ' of ' + str(len(data_filt3_0)))
print('Accuracy = ' + str(sum(data_filt3_0.VITS_late > 0)/len(data_filt3_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt3_1.VITS_late > 0)) + ' of ' + str(len(data_filt3_1)))
print('Accuracy = ' + str(sum(data_filt3_1.VITS_late > 0)/len(data_filt3_1) * 100))
print('US type = thermal stimulus')
print('N = ' + str(sum(data_filt3_2.VITS_late > 0)) + ' of ' + str(len(data_filt3_2)))
print('Accuracy = ' + str(sum(data_filt3_2.VITS_late > 0)/len(data_filt3_2) * 100))
