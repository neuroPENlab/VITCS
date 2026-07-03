#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 17:05:30 2024

@author: acalvet
"""
import pandas as pd
from os.path import join
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

path_exc = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/4_correlations_spss'
path_var = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/cluster_analysis'

vari = pd.read_excel(join(path_var, 'MVPA_dataset_pca.xlsx'), index_col=0)
patexp = pd.read_excel(join(path_exc, 'all_pat_exp.xlsx'), index_col=0)

col_our = np.where(patexp.columns.str.contains('Our_sig'))[0]
col_threat = np.where(patexp.columns.str.contains('Threat'))[0]
col_suitas = np.where(patexp.columns.str.contains('SUITAS'))[0]
col_vifs = np.where(patexp.columns.str.contains('VIFS'))[0]

vari.index = vari.index.map(lambda x: f'sub-{x}')

for nn, col_sig in zip(['our', 'threat', 'suitas', 'vifs'], [col_our, col_threat, col_suitas, col_vifs]):
    vari_patexp = vari.merge(patexp.iloc[:,col_sig], left_index=True, right_index=True)
    vari_patexp.to_excel(join(path_exc, 'SEPARADES_X_SIG', nn + '_pat_exp_var.xlsx'))
    
    res_c = pd.DataFrame(index=vari_patexp.columns[18:], columns=vari_patexp.columns[2:10])
    res_p = pd.DataFrame(index=vari_patexp.columns[18:], columns=vari_patexp.columns[2:10])
    
    for c in res_c.columns:
        for i in res_c.index:
            df_nan = vari_patexp.loc[:, [c, i]].dropna()
            res_c.loc[i, c] = pearsonr(df_nan.loc[:,c], df_nan.loc[:,i]).statistic
            res_p.loc[i, c] = pearsonr(df_nan.loc[:,c], df_nan.loc[:,i]).pvalue
            
    res_c = res_c.astype(float)
    res_p = res_p.astype(float)
    
    res_c.to_excel(join(path_exc, 'SEPARADES_X_SIG', nn + '_corr.xlsx'))
    res_p.to_excel(join(path_exc, 'SEPARADES_X_SIG', nn + '_pval.xlsx'))
    
    
    col_names = ['EMA first 2 weeks', 'DASS Stress', 'DASS Anxiety', 'DASS Depression', 'STAI-T', 'IoUS', 'SCSR-P', 'SCSR-R']
    row_names = ['CS+', 'CS-', 'CS+ - CS-', 'CS+ early', 'CS+ late', 'CS- early', 'CS- late', 'CS+ reversal', 'CS- reversal', 'CS+ - CS- reversal']
    res_c.columns = col_names
    res_c.index = row_names
    res_p.columns = col_names
    res_p.index = row_names
    
    fig, axs = plt.subplots(1, 2, figsize=(15, 8))  # Creates a 2x2 grid of subplots with a size of 10x10 inches
    sns.heatmap(res_c, ax=axs[0], cmap='coolwarm')
    axs[0].set_title('Correlation coefficient')
    sns.heatmap(res_p, ax=axs[1], vmax=0.05, cmap='crest') #, vmin=50
    axs[1].set_title('p-value')
    # plt.savefig(join(path_exc, 'SEPARADES_X_SIG', nn + '_correlations.png'))
    
    



#%%
import pandas as pd
from glob import glob

# Lista de archivos Excel (ajusta la ruta según sea necesario)
ruta_archivos = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/SVM_anxiety/EXCELS/*.xlsx'  # Cambia esta ruta a donde están tus archivos
archivos_excel = glob(ruta_archivos)

# Crear una lista para almacenar los DataFrames
dataframes = []

# Recorrer cada archivo y leerlo en un DataFrame
for archivo in sorted(archivos_excel):
    # Extraer el nombre del cuestionario del archivo (sin la extensión)
    nombre_archivo = archivo.split('/')[-1].split('.')[0]
    
    # Leer el archivo y seleccionar las columnas de interés
    df = pd.read_excel(archivo, usecols=['ID', 'IQ', 'train_test'])
    df = df.drop_duplicates(subset='ID').set_index('ID')
    # Asignar un MultiIndex a las columnas
    df.columns = pd.MultiIndex.from_product([[nombre_archivo], df.columns])
    
    # Añadir el DataFrame a la lista
    dataframes.append(df)

# Unir todos los DataFrames en uno solo, haciendo merge en el índice ID
df_final = pd.concat(dataframes, axis=1, join='outer')
df_final.to_excel('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/SVM_anxiety/EXCELS/all_subj_used.xlsx')
# Mostrar el resultado
print(df_final)

#%% 2 samples T-test between pattern expression and questionnaires (tercils)

import pandas as pd
from os.path import join
import pingouin as pg
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Outlier detection based on 3 SD
def remove_outliers(data, threshold=3):
    mean = np.mean(data)
    std = np.std(data)
    lower_bound = mean - threshold * std
    upper_bound = mean + threshold * std
    return data[(data >= lower_bound) & (data <= upper_bound)]

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask'
savedir = join(basedir,'t_test_pat_ext_var', 'matlab_subj_new')
path_exc = join(basedir, '3_sig_evaluation_test', 'results_new_CS+CS-diff') #all_sig_patexp
path_var = join(basedir, 'cluster_analysis')
path_subj_used = join(basedir, 'SVM_anxiety', 'EXCELS')

vari = pd.read_excel(join(path_var, 'MVPA_dataset_pca.xlsx'), index_col=0)
vari = vari.add_prefix("sub-", axis=0)
subj = pd.read_excel(join(path_subj_used, 'all_subj_used_used.xlsx'), index_col=0)
subj = subj.add_prefix("sub-", axis=0)
patexp = pd.read_excel(join(path_exc, 'all_pat_exp_new.xlsx'), index_col=0)

for q in subj.columns.get_level_values(0).unique():
    vari_used = vari.loc[(~np.isnan(subj[q])).index, "_".join(q.split('_')[:-1])]
    
    t_res = pd.DataFrame()
    t_res_cl = pd.DataFrame()
    for p in patexp.columns:
        if 'Our_sig' in p:
            # "All" sample
            p_inf = patexp.loc[subj[(subj[q] == -1)].index,p]
            p_sup = patexp.loc[subj[(subj[q] == 1)].index,p]
            t = pg.ttest(p_inf, p_sup)
            t['pat_exp'] = p.replace('Our_sig', 'VITS')
            t_res = pd.concat([t_res, t])
            
            p_inf_cl = remove_outliers(p_inf, threshold=3)
            p_sup_cl = remove_outliers(p_sup, threshold=3)
            
            # Perform t-test with cleaned data
            t_cl = pg.ttest(p_inf_cl, p_sup_cl)
            t_cl['pat_exp'] = p.replace('Our_sig', 'VITS')
            t_res_cl = pd.concat([t_res_cl, t_cl])
            
            fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            axes[0].boxplot([vari_used[subj[(subj[q] == -1)].index], vari_used[subj[(subj[q] == 1)].index]], labels=['Inferior = ' + str(len(p_inf)), 'Superior = ' + str(len(p_sup))])
            axes[0].set_title(q)
            axes[0].set_ylabel(q + ' values')
            axes[1].boxplot([p_inf, p_sup], labels=['Inferior = ' + str(len(p_inf)), 'Superior = ' + str(len(p_sup))])
            axes[1].set_title(p.replace('Our_sig', 'VITS'))
            axes[1].set_ylabel(p.replace('Our_sig', 'VITS') + ' values')
            axes[2].boxplot([p_inf_cl, p_sup_cl], labels=['Inferior = ' + str(len(p_inf_cl)), 'Superior = ' + str(len(p_sup_cl))])
            axes[2].set_title(p.replace('Our_sig', 'VITS') + ' cleaned')
            axes[2].set_ylabel(p.replace('Our_sig', 'VITS') + ' values')
            plt.tight_layout()
            plt.savefig(join(savedir, q + '_' + p.replace('Our_sig', 'VITS') + '_all.png'))
            
    t_res = t_res.set_index('pat_exp')
    t_res.to_excel(join(savedir, q + '.xlsx'))
    t_res_cl = t_res_cl.set_index('pat_exp')
    t_res_cl.to_excel(join(savedir, q + '_cleaned.xlsx'))
    
    
#%% 2 samples T-test between pattern expression and questionnaires (tercils) = OLD WITH (TRAIN SAMPLE TOO!!)
import pandas as pd
from os.path import join
import pingouin as pg
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Outlier detection based on 3 SD
def remove_outliers(data, threshold=3):
    mean = np.mean(data)
    std = np.std(data)
    lower_bound = mean - threshold * std
    upper_bound = mean + threshold * std
    return data[(data >= lower_bound) & (data <= upper_bound)]

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask'
savedir = join(basedir,'t_test_pat_ext_var', 'matlab_subj_new')
path_exc = join(basedir, '3_sig_evaluation_test', 'results_new_CS+CS-diff') #all_sig_patexp
path_var = join(basedir, 'cluster_analysis')
path_subj_used = join(basedir, 'SVM_anxiety', 'EXCELS')

vari = pd.read_excel(join(path_var, 'MVPA_dataset_pca.xlsx'), index_col=0)
vari = vari.add_prefix("sub-", axis=0)
subj = pd.read_excel(join(path_subj_used, 'all_subj_used.xlsx'), header=[0, 1], index_col=0)
subj = subj.add_prefix("sub-", axis=0)
patexp = pd.read_excel(join(path_exc, 'all_pat_exp_new.xlsx'), index_col=0)

for q in subj.columns.get_level_values(0).unique():
    vari_used = vari.loc[(~np.isnan(subj[q].IQ)).index, "_".join(q.split('_')[:-1])]
    
    t_res = pd.DataFrame()
    t_res_cl = pd.DataFrame()
    for p in patexp.columns:
        if 'Our_sig' in p:
            # "All" sample
            p_inf = patexp.loc[subj[(subj[q].IQ == -1)].index,p]
            p_sup = patexp.loc[subj[(subj[q].IQ == 1)].index,p]
            t = pg.ttest(p_inf, p_sup)
            t['pat_exp'] = p.replace('Our_sig', 'VITS')
            t_res = pd.concat([t_res, t])
            
            p_inf_cl = remove_outliers(p_inf, threshold=3)
            p_sup_cl = remove_outliers(p_sup, threshold=3)
            
            # Perform t-test with cleaned data
            t_cl = pg.ttest(p_inf_cl, p_sup_cl)
            t_cl['pat_exp'] = p.replace('Our_sig', 'VITS')
            t_res_cl = pd.concat([t_res_cl, t_cl])
            
            fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            axes[0].boxplot([vari_used[subj[(subj[q].IQ == -1)].index], vari_used[subj[(subj[q].IQ == 1)].index]], labels=['Inferior = ' + str(len(p_inf)), 'Superior = ' + str(len(p_sup))])
            axes[0].set_title(q)
            axes[0].set_ylabel(q + ' values')
            axes[1].boxplot([p_inf, p_sup], labels=['Inferior = ' + str(len(p_inf)), 'Superior = ' + str(len(p_sup))])
            axes[1].set_title(p.replace('Our_sig', 'VITS'))
            axes[1].set_ylabel(p.replace('Our_sig', 'VITS') + ' values')
            axes[2].boxplot([p_inf_cl, p_sup_cl], labels=['Inferior = ' + str(len(p_inf_cl)), 'Superior = ' + str(len(p_sup_cl))])
            axes[2].set_title(p.replace('Our_sig', 'VITS') + ' cleaned')
            axes[2].set_ylabel(p.replace('Our_sig', 'VITS') + ' values')
            plt.tight_layout()
            plt.savefig(join(savedir, q + '_' + p.replace('Our_sig', 'VITS') + '_all.png'))
            
    t_res = t_res.set_index('pat_exp')
    t_res.to_excel(join(savedir, q + '.xlsx'))
    t_res_cl = t_res_cl.set_index('pat_exp')
    t_res_cl.to_excel(join(savedir, q + '_cleaned.xlsx'))
#%%     
    
    iq = np.quantile(vari_nan[q], [1/3, 2/3])
    if not np.any(vari_nan[q] < iq[0]):
        inf = vari_nan[vari_nan[q] <= iq[0]][q]
    else:
        inf = vari_nan[vari_nan[q] < iq[0]][q]
    if not np.any(vari_nan[q] > iq[1]):
        sup = vari_nan[vari_nan[q] >= iq[1]][q]
    else:
        sup = vari_nan[vari_nan[q] > iq[1]][q]
    t_res = pd.DataFrame()
    for p in patexp.columns:
        if 'Our_sig' in p:
            t = pg.ttest(patexp.loc[inf.index,p], patexp.loc[sup.index,p])
            t['pat_exp'] = p.replace('Our_sig', 'VITS')
            t_res = pd.concat([t_res, t])
            
            fig, axes = plt.subplots(1, 2, figsize=(8, 4))
            axes[0].boxplot([inf, sup], labels=['Inferior = ' + str(len(inf)), 'Superior = ' + str(len(sup))])
            axes[0].set_title(q)
            axes[0].set_ylabel(q + ' values')
            axes[1].boxplot([patexp.loc[inf.index,p], patexp.loc[sup.index,p]], labels=['Inferior', 'Superior'])
            axes[1].set_title(p.replace('Our_sig', 'VITS'))
            axes[1].set_ylabel(p.replace('Our_sig', 'VITS') + ' values')
            plt.tight_layout()
            plt.savefig(join(basedir, 't_test_pat_ext_var', q + '_' + p.replace('Our_sig', 'VITS') + '.png'))
    t_res = t_res.set_index('pat_exp')
    t_res.to_excel(join(basedir, 't_test_pat_ext_var', q + '.xlsx'))
            
