#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 10:12:42 2024

@author: acalvet
"""
import pandas as pd
from os.path import join
import glob
import os

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/ENIGMA_FC'
excel = pd.read_csv(join(basedir, 'ENIGMA_FC_clean_QCpassed1&2_combat.csv'))

list_subj = []
age = []
sex = []
group = []
diagnosis = []
dataset = []
CS_type = []
US_type = []
pair_rate = []

for idx, row in excel.iterrows():
    path = join(basedir, 'CONDITIONING')
    if len(row.Group_Dataset.split('_')) > 2:
        path = join(path, row.Group_Dataset.split('_')[0] + '_' + row.Group_Dataset.split('_')[1], row.Group_Dataset)
    else:
        path = join(path, row.Group_Dataset, row.Group_Dataset)
        
    if not os.path.exists(path):
        print('NO EXISTEIX ' + path)
    
    if '.gz' in row.effect_path:
        if os.path.exists(path + '/halfpipe' + row.effect_path.split('halfpipe')[1][:-3]):
            path = path + '/halfpipe' + row.effect_path.split('halfpipe')[1][:-3]
        # if '.gz' in row.effect_path and not os.path.exists(path + '/halfpipe' + row.effect_path.split('halfpipe')[1][:-3]):
        #     os.system('fslchfiletype NIFTI ' + path + '/halfpipe' + row.effect_path.split('halfpipe')[1])
        #     path = path + '/halfpipe' + row.effect_path.split('halfpipe')[1][:-3]
        # elif '.gz' in row.effect_path:
        #     path = path + '/halfpipe' + row.effect_path.split('halfpipe')[1][:-3]
        elif os.path.exists(path + '/halfpipe' + row.effect_path.split('halfpipe')[1]):
            path = path + '/halfpipe' + row.effect_path.split('halfpipe')[1]
    if os.path.isfile(path):
        list_subj.append(path)
        age.append(row.Age)
        sex.append(row.Sex)
        group.append(row.Healthy_or_patient)
        diagnosis.append(row.Principal_diagnosis_current)
        dataset.append(row.Group_Dataset)
        CS_type.append(row.CS_used)
        US_type.append(row.US_type)
        pair_rate.append(row['Reinforcing_rate....'])
    else:
        print('ALERTA!!! NO EXISTEIX ' + path)


# for idx, row in excel.iterrows():
#     path = join(basedir, 'CONDITIONING')
#     if len(row.Group_Dataset.split('_')) > 2:
#         path = join(path, row.Group_Dataset.split('_')[0] + '_' + row.Group_Dataset.split('_')[1], row.Group_Dataset)
#     else:
#         path = join(path, row.Group_Dataset, row.Group_Dataset)
        
#     if not os.path.exists(path):
#         print('NO EXISTEIX ' + path)
        
#     if os.path.exists(join(path, 'halfpipe', row.SubjectID_neuroimatge, 'func')):
#         path = join(path, 'halfpipe', row.SubjectID_neuroimatge, 'func')
#         # if len(glob.glob(join(path, '*'))) > 1 and len(glob.glob(join(path, '*.nii*'))) == 0:
#         #     print("ALERTA MÉS D'UNA TASK en " + path)
#         #     tsk = sorted(glob.glob(join(path, '*')))[0]
#         #     path = glob.glob(join(tsk, row.SubjectID_neuroimatge + '*task*_stat-effect_statmap.nii*'))[0]
#         # elif len(glob.glob(join(path, '*'))) > 1 and len(glob.glob(join(path, '*.nii*'))) > 0:
#             # path = glob.glob(join(path, row.SubjectID_neuroimatge + '*task*_stat-effect_statmap.nii*'))[0]
#         # else:
#             # path = glob.glob(join(path, '*', row.SubjectID_neuroimatge + '*task*_stat-effect_statmap.nii*'))[0]
#         if os.path.exists(path + row.effect_path.split('func')[1]):
#             if '.gz' in row.effect_path and not os.path.exists(path + row.effect_path.split('func')[1][:-3]):
#                 os.system('fslchfiletype NIFTI ' + path + row.effect_path.split('func')[1])
#                 path = path + row.effect_path.split('func')[1][:-3]
#             else:
#                 path = path + row.effect_path.split('func')[1][:-3]
#         if os.path.isfile(path):
#             list_subj.append(path)
#             age.append(row.Age)
#             sex.append(row.Sex)
#             group.append(row.Healthy_or_patient)
#             diagnosis.append(row.Principal_diagnosis_current)
#             dataset.append(row.Group_Dataset)
#         else:
#             print('ALERTA!!! NO EXISTEIX ' + path)
#     else:
#         path = sorted(glob.glob(join(path, 'halfpipe', row.SubjectID_neuroimatge, '*', 'func')))[0]
#         if len(glob.glob(join(path, '*'))) > 1 and len(glob.glob(join(path, '*.nii*'))) == 0:
#             print("ALERTA MÉS D'UNA TASK")
#         path = glob.glob(join(path, '*', row.SubjectID_neuroimatge + '*task*_stat-effect_statmap.nii*'))[0]
#         if os.path.isfile(path):
#             list_subj.append(path)
#             age.append(row.Age)
#             sex.append(row.Sex)
#             group.append(row.Healthy_or_patient)
#             diagnosis.append(row.Principal_diagnosis_current)
#             dataset.append(row.Group_Dataset)
#         else:
#             print('ALERTA!!! NO EXISTEIX ' + path)


data_subj = pd.DataFrame({'path': list_subj, 'age': age, 'sex': sex, 'group': group, 'diagnosis': diagnosis, 
                          'dataset': dataset, 'CS_type': CS_type, 'US_type': US_type, 'pair_rate': pair_rate})
data_subj.to_excel(join(basedir, 'path_info_subj_moreinfo.xlsx'))
