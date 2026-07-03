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


#%%
name_dataset = []
acc_dataset = []
num_dataset = []
dataset_num = {}
for n, dataset in enumerate(data.dataset.unique()):
    subdata = data[data.dataset == dataset]
    
    # accuracy = values>0 / N total
    name_dataset.append(dataset)
    acc = sum(subdata.VITS > 0)/len(subdata) * 100
    acc_dataset.append(acc)
    num_dataset.append(n+1)
    dataset_num[dataset] = n+1

dataset_accuracies = pd.DataFrame()
dataset_accuracies.loc[:,'dataset'] = name_dataset
dataset_accuracies.loc[:,'dataset_num'] = num_dataset
dataset_accuracies.loc[:,'acc'] = acc_dataset
dataset_accuracies = dataset_accuracies.set_index('dataset')

bad_k_datasets = [7]
bad_k20_datasets = [5, 8]
bad_T_datasets = [11, 30, 33]
bad_T55_datasets = [19, 25, 32] # entre 5.5 i 6
bad_both_datasets = [16, 20, 27, 34]
bad_datasets = [7, 16, 20, 27, 34, 11, 30, 33]
bad_bad_datasets = [7, 16, 20, 27, 34, 11, 30, 33, 19, 25, 32]

#colors = ['lightcoral' if i in bad_datasets else 'skyblue' for i in num_dataset]
colors = [
    'tomato' if i in bad_k_datasets else
    'lightcoral' if i in bad_k20_datasets else
    '#9370DB' if i in bad_T_datasets else
    '#D8BFD8' if i in bad_T55_datasets else
    '#2F2F2F' if i in bad_both_datasets else
    'skyblue'
    for i in num_dataset
]

fig, ax = plt.subplots(1, 1, figsize=(20, 10))
plt.bar(dataset_accuracies.dataset_num.astype(str), dataset_accuracies.acc, capsize=5, alpha=0.90, color=colors)
plt.xlabel('Dataset number', fontsize=22)
plt.ylabel('Accuracy (%)', fontsize=22)
plt.title('SUITAS', fontsize=26)
plt.xticks(fontsize=16) #, rotation=45, ha='right', rotation_mode='anchor'
plt.yticks(fontsize=16)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.ylim(0, 105)
plt.show()


####### FILTRATGE 1
dataset_accuracies_filter1 = dataset_accuracies[~dataset_accuracies.dataset_num.isin(bad_datasets)]
dataset_accuracies_filter1.loc[:,'dataset_num_new'] = range(1, len(dataset_accuracies_filter1)+1)

# Fer el plot
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
plt.bar(dataset_accuracies_filter1.dataset_num_new.astype(str), dataset_accuracies_filter1.acc, capsize=5, alpha=0.90, color='skyblue')
plt.xlabel('Dataset number', fontsize=22)
plt.ylabel('Accuracy (%)', fontsize=22)
plt.title('SUITAS', fontsize=26)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

colors2 = [
    '#D8BFD8' if int(i) in bad_T55_datasets else
    'skyblue'
    for i in dataset_accuracies_filter1.dataset_num
]
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
plt.bar(dataset_accuracies_filter1.dataset_num_new.astype(str), dataset_accuracies_filter1.acc, capsize=5, alpha=0.90, color=colors2)
plt.xlabel('Dataset number', fontsize=22)
plt.ylabel('Accuracy (%)', fontsize=22)
plt.title('SUITAS', fontsize=26)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

data_filter1 = data[data.dataset.isin(dataset_accuracies_filter1.index)]
data_2groups_f1 = data_filter1.groupby('dataset').filter(lambda x: x['group'].nunique() == 2)
data_2sex_f1 = data_filter1.groupby('dataset').filter(lambda x: x['sex'].nunique() == 2)

# MAN - WOMAN ?? -- estan els datasets guardats!!
# HEALTHY - NON-HEALTHY ??

# Separated by diagnostic
output_file = join(basedir, "t_test_results.txt")
with open(output_file, "w") as f:
    f.write("T-Test Results\n")
    f.write("=" * 50 + "\n\n")

    data_2groups2 = data_2groups_f1
    for diag in data_2groups2.diagnosis.unique():
        if diag != 'not applicable':
            stats = []
            subdata_diagnosis = data_2groups2[data_2groups2.diagnosis == diag]
            subdata_healthy = data_2groups2[data_2groups2.diagnosis == 'not applicable']
            
            for dataset in subdata_diagnosis.dataset.unique():
                if len(subdata_diagnosis[subdata_diagnosis.dataset == dataset]) > 1:
                    data_patient = subdata_diagnosis[subdata_diagnosis.dataset == dataset].VITS
                    data_healthy = subdata_healthy[subdata_healthy.dataset == dataset].VITS
                    if len(data_patient) > 5 and len(data_healthy) > 5:
                        mean_patient = data_patient.mean()
                        sem_patient = sem(data_patient, nan_policy='omit')
                        mean_healthy = data_healthy.mean()
                        sem_healthy = sem(data_healthy, nan_policy='omit')
                        
                        # t-test
                        t_stat, p_value = ttest_ind(data_patient, data_healthy, nan_policy='omit', equal_var=False)
                        
                        stats.append({'dataset': dataset_num[dataset], 'diagnostic': diag, 'mean_patient': mean_patient, 
                                      'sem_patient': sem_patient, 'mean_healthy': mean_healthy, 'sem_healthy': sem_healthy,
                                      't_stat': t_stat, 'p_value': p_value, 'n_patient': len(data_patient), 'n_healthy': len(data_healthy)})
                        
            if stats != []:
                stats_df = pd.DataFrame(stats)
                
                f.write(f"Results for {diag.upper()}:\n")
                f.write(stats_df[['dataset', 'n_patient', 'n_healthy', 't_stat', 'p_value']].to_string(index=False))
                f.write("\n\n" + "=" * 50 + "\n\n")
                
                fig, ax = plt.subplots(1, 1, figsize=(12, 8))
                bar_width = 0.35
                x_indexes = np.arange(len(stats_df['dataset']))
                
                # Plot para healthy
                ax.bar(
                    x_indexes - bar_width / 2,
                    stats_df['mean_healthy'],
                    yerr=stats_df['sem_healthy'],
                    capsize=5,
                    alpha=0.75,
                    width=bar_width,
                    label='Healthy',
                    color='skyblue'
                )
        
                # Plot para patient
                ax.bar(
                    x_indexes + bar_width / 2,
                    stats_df['mean_patient'],
                    yerr=stats_df['sem_patient'],
                    capsize=5,
                    alpha=0.75,
                    width=bar_width,
                    label='Patient',
                    color='orange'
                )
        
                # Personalizar el gráfico
                ax.set_title(f'Pattern expression from VITS per Dataset and Group ({diag.upper()})', fontsize=16)
                ax.set_xlabel('Dataset', fontsize=14)
                ax.set_ylabel('Mean pattern expression VITS ± SEM', fontsize=14)
                ax.set_xticks(x_indexes)
                ax.set_xticklabels(stats_df['dataset'], fontsize=12) #, rotation=45
                ax.legend(title='Group', fontsize=12, title_fontsize=14)
                ax.grid(axis='y', linestyle='--', alpha=0.7)
        
                plt.tight_layout()
                plt.show()

####### FILTRATGE 2
filtered_data2 = [
    (n, a) for n, a in zip(num_dataset, acc_dataset)
    if n not in bad_bad_datasets
]
filtered_num_dataset2 = [str(n) for n, _ in filtered_data2]
filtered_acc_dataset2 = [a for _, a in filtered_data2]

# Fer el plot
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
# plt.bar(filtered_num_dataset, filtered_acc_dataset, capsize=5, alpha=0.90, color='skyblue')
plt.bar([f"{i}" for i in range(1,len(filtered_acc_dataset2)+1)], filtered_acc_dataset2, capsize=5, alpha=0.90, color='skyblue')
plt.xlabel('Dataset number', fontsize=22)
plt.ylabel('Accuracy (%)', fontsize=22)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


#%%##### NOVA FORMA DE FER-HO! --- A NIVELL DE SUBJECTE, NO DATASET
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

### CHECK datasets Barcelona_Cardoner (26 GAD, 45 HC) and Vanderbilt_Kaczkurkin (28 PTSD, 53 HC)

data_BCN_Card = data[data.dataset == 'Barcelona_Cardoner']
sum(data_BCN_Card.VITS > 0)/len(data_BCN_Card.VITS)

data_BCN_Card_HC = data_BCN_Card.loc[data_BCN_Card.group == 'healthy', 'VITS']
sum(data_BCN_Card_HC > 0)/len(data_BCN_Card_HC)

data_BCN_Card_GAD = data_BCN_Card.loc[data_BCN_Card.group == 'patient', 'VITS']
sum(data_BCN_Card_GAD > 0)/len(data_BCN_Card_GAD)

plt.figure(figsize=(4,5))
plt.boxplot([data_BCN_Card_HC, data_BCN_Card_GAD], widths=0.5, meanline=True, meanprops=dict(color='black', linewidth=2), 
            medianprops=dict(color='black', linewidth=2))
for i, data in enumerate([data_BCN_Card_HC, data_BCN_Card_GAD]):
    x = np.random.normal(i+1, 0.04, size=len(data))
    plt.scatter(x, data, alpha=0.7, s=25)
plt.xticks([1,2], ['HC', 'GAD'])
plt.ylabel('VITS')
plt.tight_layout()
plt.show()

data_Vand = data[data.dataset == 'Vanderbilt_Kaczkurkin']
data_Vand_HC = data_Vand.loc[data_Vand.group == 'healthy', 'VITS']
data_Vand_PTSD = data_Vand.loc[data_Vand.diagnosis == 'ptsd', 'VITS']

plt.figure(figsize=(4,5))
plt.boxplot([data_Vand_HC, data_Vand_PTSD], widths=0.5, meanline=True, meanprops=dict(color='black', linewidth=2), 
            medianprops=dict(color='black', linewidth=2))
for i, data in enumerate([data_Vand_HC, data_Vand_PTSD]):
    x = np.random.normal(i+1, 0.04, size=len(data))
    plt.scatter(x, data, alpha=0.7, s=25)
plt.xticks([1,2], ['HC', 'PTSD'])
plt.ylabel('VITS')
plt.tight_layout()
plt.show()

# SEPARATE BY DATASET!
us_type = ['electric shock', 'auditory stimulus']
for dset in QC_dataset_filt1.index:
    df_dset = data_filt1[data_filt1.dataset == dset]
    print('\n' + dset + '\nUS type = ' + us_type[int(np.unique(df_dset.US_type)[0])] + '; Reinforcement rate = ' + str(np.unique(df_dset.pair_rate)[0]) + '%')
    print('N = ' + str(sum(df_dset.VITS > 0)) + ' of ' + str(len(df_dset)))
    print('Accuracy = ' + str(sum(df_dset.VITS > 0)/len(df_dset) * 100))
# ho podem fer amb un loop

print('Reinforcement rate = 31%')
print('N = ' + str(sum(data_filt1_31.VITS > 0)) + ' of ' + str(len(data_filt1_31)))
print('Accuracy = ' + str(sum(data_filt1_31.VITS > 0)/len(data_filt1_31) * 100))
print('Reinforcement rate = 33%')
print('N = ' + str(sum(data_filt1_33.VITS > 0)) + ' of ' + str(len(data_filt1_33)))
print('Accuracy = ' + str(sum(data_filt1_33.VITS > 0)/len(data_filt1_33) * 100))
print('Reinforcement rate = 40%')
print('N = ' + str(sum(data_filt1_40.VITS > 0)) + ' of ' + str(len(data_filt1_40)))
print('Accuracy = ' + str(sum(data_filt1_40.VITS > 0)/len(data_filt1_40) * 100))
print('Reinforcement rate = 50%')
print('N = ' + str(sum(data_filt1_50.VITS > 0)) + ' of ' + str(len(data_filt1_50)))
print('Accuracy = ' + str(sum(data_filt1_50.VITS > 0)/len(data_filt1_50) * 100))
print('Reinforcement rate = 55%')
print('N = ' + str(sum(data_filt1_55.VITS > 0)) + ' of ' + str(len(data_filt1_55)))
print('Accuracy = ' + str(sum(data_filt1_55.VITS > 0)/len(data_filt1_55) * 100))
print('Reinforcement rate = 62.5%')
print('N = ' + str(sum(data_filt1_625.VITS > 0)) + ' of ' + str(len(data_filt1_625)))
print('Accuracy = ' + str(sum(data_filt1_625.VITS > 0)/len(data_filt1_625) * 100))
print('Reinforcement rate = 80%')
print('N = ' + str(sum(data_filt1_80.VITS > 0)) + ' of ' + str(len(data_filt1_80)))
print('Accuracy = ' + str(sum(data_filt1_80.VITS > 0)/len(data_filt1_80) * 100))
print('Reinforcement rate = 100%')
print('N = ' + str(sum(data_filt1_100.VITS > 0)) + ' of ' + str(len(data_filt1_100)))
print('Accuracy = ' + str(sum(data_filt1_100.VITS > 0)/len(data_filt1_100) * 100))

## REINFORCEMENT RATE NO TÉ CAP EFECTE!!!!!!!!!


data_filt2 = data[data.dataset.isin(QC_dataset_filt2.index)]
data_filt2_0 = data_filt2[data_filt2.US_type == 0]
data_filt2_1 = data_filt2[data_filt2.US_type == 1]
print('ALL DATA')
print('N = ' + str(sum(data_filt2.VITS > 0)) + ' of ' + str(len(data_filt2)))
print('Accuracy = ' + str(sum(data_filt2.VITS > 0)/len(data_filt2) * 100))
print('US type = electric shock')
print('N = ' + str(sum(data_filt2_0.VITS > 0)) + ' of ' + str(len(data_filt2_0)))
print('Accuracy = ' + str(sum(data_filt2_0.VITS > 0)/len(data_filt2_0) * 100))
print('US type = auditory stimulus')
print('N = ' + str(sum(data_filt2_1.VITS > 0)) + ' of ' + str(len(data_filt2_1)))
print('Accuracy = ' + str(sum(data_filt2_1.VITS > 0)/len(data_filt2_1) * 100))

# N>=20; T>=6,   kmax>=20  --> 1523/1790; acc = 85%
# N>=15; T>=6,   kmax>=20  --> 1541/1808; acc = 85%
# N>=15; T>=5.5, kmax>=20  --> 1641/1950; acc = 84%
# N>=15; T>=5,   kmax>=20  --> 1723/2094; acc = 82%

# N>=15; T>=8,   kmax>=20  --> 1047/1152; acc = 91% (16 datasets)
# N>=15; T>=7,   kmax>=20  --> 1295/1471; acc = 88% (21 datasets)

# FINAL DECISION:
# N>=15; T>=6,   kmax>=20  --> 1541/1808; acc = 85% (26 datasets)
# N>=15; T>=6.6, kmax>=20  --> 1350/1553; acc = 87% (20 datasets) -- numero més rodó
# N>=20; T>=7.75, kmax>=20  --> 1074/1185; acc = 91% (15 datasets) -- numero més rodó

# FINAL DECISION (NOVA SIGNATURA):
# N>=15; T>=6,   kmax>=20  --> 1545/1808; acc = 85% (26 datasets)
# N>=15; T>=6.6, kmax>=20  --> 1351/1553; acc = 87% (20 datasets) -- numero més rodó
# N>=20; T>=7.75, kmax>=20  --> 1075/1185; acc = 91% (15 datasets) -- numero més rodó

# FINAL DECISION (NOVA SIGNATURA 2):
# N>=15; T>=6,   kmax>=20  --> 1546/1808; acc = 86% (26 datasets)
# N>=15; T>=6.6, kmax>=20  --> 1352/1553; acc = 87% (20 datasets) -- numero més rodó
# N>=20; T>=7.75, kmax>=20  --> 1076/1185; acc = 91% (15 datasets) -- numero més rodó

# SEPARATE BY HEALTHY and PATIENT
acc_dataset_group_2 = pd.DataFrame(acc_dataset_group).set_index('dataset')
acc_dataset_group_2 = acc_dataset_group_2.drop(index=acc_dataset_group_2.index.intersection(bad_datasets))
acc_dataset_sex_2 = pd.DataFrame.from_dict(acc_dataset_sex).set_index('dataset')
acc_dataset_sex_2 = acc_dataset_sex_2.drop(index=acc_dataset_sex_2.index.intersection(bad_datasets))

fig, ax = plt.subplots(1, 1, figsize=(20, 10))
sns.barplot(data=acc_dataset_group_2, x='dataset', y='acc', hue='group', palette='husl', ax=ax)
plt.xlabel('Dataset number', fontsize=22)
plt.ylabel('Accuracy (%)', fontsize=22)
plt.xticks(fontsize=16) #, rotation=45, ha='right', rotation_mode='anchor'
plt.yticks(fontsize=16)
plt.title('Accuracy per Dataset and Group', fontsize=24)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title='Group', fontsize=14, title_fontsize=16)
plt.tight_layout()
plt.show()

# SEPARATE BY SEX
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
sns.barplot(data=acc_dataset_sex_2, x='dataset', y='acc', hue='sex', palette='husl', ax=ax)
plt.xlabel('Dataset number', fontsize=22)
plt.ylabel('Accuracy (%)', fontsize=22)
plt.xticks(fontsize=16) #, rotation=45, ha='right', rotation_mode='anchor'
plt.yticks(fontsize=16)
plt.title('Accuracy per Dataset and Sex', fontsize=24)
plt.grid(axis='y', linestyle='--', alpha=0.7)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, ['Man', 'Woman'], title='Sex', fontsize=14, title_fontsize=16)
plt.tight_layout()
plt.show()

# SAVE RESULTS
df_acc_all_datasets = pd.DataFrame(acc_dataset, index=[num_dataset], columns=['accuracy'])
df_acc_all_datasets.to_excel(join(basedir, 'acc_datasets_all.xlsx'))
df_acc_datasets_bygroup.to_excel(join(basedir, 'acc_datasets_bygroup.xlsx'))
df_acc_datasets_bysex.to_excel(join(basedir, 'acc_datasets_bysex.xlsx'))