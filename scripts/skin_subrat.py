#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:35:05 2025

@author: acalvet

Analyze skin conductance and subjective ratings
"""
from os.path import join
import pandas as pd
from scipy.stats import spearmanr, pearsonr, ttest_rel
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import seaborn as sns

def within_subjects_sem(df, conditions):
    """Calcula el error estándar corregido dentro de sujetos."""
    subject_means = df[conditions].mean(axis=1)  # Media por sujeto
    df_centered = df[conditions].subtract(subject_means, axis=0)  # Centrar datos
    corrected_sem = df_centered.std(ddof=1) / np.sqrt(len(df))  # SEM corregido
    return corrected_sem

basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask'

patexp = pd.read_excel(join(basedir, '3_sig_evaluation_test', 'results_new_CS+CS-diff', 'all_pat_exp_new.xlsx'), index_col=0)
# nomes volem VITS - filtrat i canviar nom
# patexp = patexp.loc[:,patexp.columns.str.startswith('Our_sig')]
# patexp.columns = patexp.columns.str.replace('Our_sig', 'VITS')
patexp = patexp.loc[:,patexp.columns.str.startswith('VITS')]
patexp.index = patexp.index.str.replace('sub-', '', regex=True)
skin = pd.read_excel(join(basedir, 'SKIN_ARO_VAL', 'SCR_FISAX_NORMALIZED_03_11_2022.xlsx'), index_col=0)
skin = skin.loc[patexp.index.intersection(skin.index),:]
subj_rat = pd.read_excel(join(basedir, 'SKIN_ARO_VAL', 'Subjective_ratings_condrev.xlsx'), index_col=0)
subj_rat = subj_rat.iloc[:, 4:]
subj_rat = subj_rat.iloc[:, [1, 0, 3, 2, 5, 4, 7, 6]]
subj_rat = subj_rat.loc[patexp.index.intersection(subj_rat.index),:]
val_cols = [0, 1, 4, 5]
aro_cols = [2, 3, 6, 7]
# load condition order
order = pd.read_excel(join(basedir, 'SKIN_ARO_VAL', 'Conditioning_Reversal_order_of_trials.xlsx'), index_col=0) 

#%%###################################### SUBJECTIVE RATINGS #########################################
subj_rat[subj_rat.filter(like='_VAL').columns] = (subj_rat[subj_rat.filter(like='_VAL').columns] - 6) * -1

means_aro = subj_rat.iloc[:,aro_cols].mean(axis=0, skipna=True)
errors_aro = within_subjects_sem(subj_rat, subj_rat.iloc[:, aro_cols].columns)
#errors_aro = subj_rat.iloc[:,aro_cols].apply(lambda x: sem(x, nan_policy='omit'), axis=0) -- across subjects
means_val = subj_rat.iloc[:,val_cols].mean(axis=0, skipna=True)
errors_val = within_subjects_sem(subj_rat, subj_rat.iloc[:, val_cols].columns)
#errors_val = subj_rat.iloc[:,val_cols].apply(lambda x: sem(x, nan_policy='omit'), axis=0) -- across subjects

t_tests = [['COND_CSplus_ARO', 'COND_Csminus_ARO'], ['REV_New_CSplus_ARO', 'REV_New_CSminus_ARO'],
           ['COND_CSplus_ARO', 'REV_New_CSplus_ARO'], ['COND_Csminus_ARO', 'REV_New_CSminus_ARO'],
           ['COND_CSplus_VAL', 'COND_CSminus_VAL'], ['REV_New_Csplus_VAL', 'REV_New_CSminus_VAL'],
           ['COND_CSplus_VAL', 'REV_New_Csplus_VAL'], ['COND_CSminus_VAL', 'REV_New_CSminus_VAL']]

for test in t_tests:
    t, p = ttest_rel(subj_rat.loc[:, test[0]], subj_rat.loc[:, test[1]])
    print(test)
    print('T-statistic = ' + str(t) + '   p-value = ' + str(p) + '\n')

colors = ['#1f77b4', '#ffd307', '#aec7e8', '#ffdf69'] # 'skyblue', 'lightcoral', 'gold', 'lightgreen', 'mediumpurple'
leg = ['CS+ cond.', 'CS- cond.', 'CS+ rev.', 'CS- rev.']

fig, ax = plt.subplots(1, 2, figsize=(16, 6))
ax[0].bar(subj_rat.iloc[:,aro_cols].columns, means_aro, yerr=errors_aro, capsize=5, alpha=0.75, color=colors)
ax[0].set_ylabel('Mean value rating', fontsize=22)
ax[0].set_title('AROUSAL', fontsize=22)
ax[0].set_xticklabels(leg, fontsize=18)
ax[0].grid(axis='y', linestyle='--', alpha=0.7)
ax[0].tick_params(axis='y', labelsize=18)
ymax = means_aro.max() + 0.2
ax[0].plot([0, 0, 1, 1], [ymax, ymax + 0.15, ymax + 0.15, ymax], lw=1.5, color='k')
ax[0].text(0.5, ymax + 0.2, "***", ha='center', fontsize=14) # bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
ax[0].plot([2, 2, 3, 3], [ymax, ymax + 0.15, ymax + 0.15, ymax], lw=1.5, color='k')
ax[0].text(2.5, ymax + 0.2, "***", ha='center', fontsize=14)
ax[0].set_ylim((0,5))

ax[1].bar(subj_rat.iloc[:,val_cols].columns, means_val, yerr=errors_val, capsize=5, alpha=0.75, color=colors)
ax[1].set_ylabel('Mean value rating', fontsize=22)
ax[1].set_title('VALENCE (negative)', fontsize=22)
# ax[1].set_xticklabels(subj_rat.iloc[:,val_cols].columns, rotation=45, ha='right', rotation_mode='anchor', fontsize=16)
ax[1].set_xticklabels(leg, fontsize=18)
ax[1].grid(axis='y', linestyle='--', alpha=0.7)
ax[1].tick_params(axis='y', labelsize=18)
ymax = means_val.max() + 0.2
ax[1].plot([0, 0, 1, 1], [ymax, ymax + 0.15, ymax + 0.15, ymax], lw=1.5, color='k')
ax[1].text(0.5, ymax + 0.2, "***", ha='center', fontsize=14) # bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
ax[1].plot([2, 2, 3, 3], [ymax, ymax + 0.15, ymax + 0.15, ymax], lw=1.5, color='k')
ax[1].text(2.5, ymax + 0.2, "***", ha='center', fontsize=14)
ax[1].set_ylim((0,5))
plt.tight_layout()
plt.show()

#%%####################################### SKIN CONDUCTANCE ##########################################

### ORDER ###
p = 1
m = 1
trial_by_trial = []
for c, row in order.iterrows():
    if 'Baseline' in c:
        if row.STIMULUS == 'CS+':
            trial_by_trial.append('BL_CSplus_trial_' + str(p))
            p = p + 1
            if p > 5: p = 1
        elif row.STIMULUS == 'CS-':
            trial_by_trial.append('BL_CSminus_trial' + str(m))
            m = m + 1
            if m > 5: m = 1
    elif 'Conditioning' in c:
        if row.STIMULUS == 'CS+':
            trial_by_trial.append('Cond_CSplus_trial' + str(p))
            p = p + 1
            if p > 10: p = 1
        elif row.STIMULUS == 'CS-':
            trial_by_trial.append('Cond_Csminus_trial' + str(m))
            m = m + 1
            if m > 10: m = 1
    elif 'Rev' in c:
        if row.STIMULUS == 'NewCS+':
            trial_by_trial.append('REV_New_CSplus_trial' + str(p))
            p = p + 1
            if p > 10: p = 1
        elif row.STIMULUS == 'NewCS-':
            trial_by_trial.append('REV_New_CSminus_trial' + str(m))
            m = m + 1
            if m > 10: m = 1

skin_trialbytrial = skin[trial_by_trial]

ax = skin_trialbytrial.T.plot(legend=False, figsize=(30,20))
ax.set_xticks(range(len(skin_trialbytrial.columns)))
ax.set_xticklabels(skin_trialbytrial.columns, rotation=45, ha='right', fontsize=18)
ax.tick_params(axis='y', labelsize=18)
ax.set_xlabel("Trials", fontsize=22)
ax.set_ylabel("Values", fontsize=22)
ax.set_title("Skin Conductance Trial by Trial", fontsize=26)
plt.grid(True)
plt.show()

## ONLY CONDITIONING AND REVERSAL (without baseline) = .iloc[:,10:]
mean_values = skin_trialbytrial.mean(axis=0)
q1 = skin_trialbytrial.quantile(0.25, axis=0)
q3 = skin_trialbytrial.quantile(0.75, axis=0)

# Calcular la regressió lineal
reg = LinearRegression().fit(np.arange(1, len(mean_values)+1).reshape(-1, 1), mean_values.values.reshape(-1, 1))
trend = reg.predict(np.arange(1, len(mean_values)+1).reshape(-1, 1))

fig, ax = plt.subplots(figsize=(20, 10))
ax.plot(mean_values.index[10:], mean_values.values[10:], color='b', linewidth=3, label='Mean')
ax.fill_between(mean_values.index[10:], q1.values[10:], q3.values[10:], color='b', alpha=0.2, label='IQR (Q1-Q3)')
ax.plot(mean_values.index[10:], trend[10:], label="Trend (Regression)", linestyle="--", color="red")
ax.set_xticks(range(len(mean_values.index[10:])))
ax.set_xticklabels(mean_values.index[10:], rotation=45, ha='right', fontsize=14)
ax.set_xlabel("Trials", fontsize=18)
ax.set_ylabel("Values", fontsize=18)
ax.set_title("Skin Conductance (Mean ± IQR)", fontsize=22)
ax.legend(fontsize=14)
plt.grid(True, linestyle="--", alpha=0.7)
plt.show()

correlation, p_value = spearmanr(mean_values, range(len(mean_values)))
print(f"Spearman Correlation: {correlation}, p-value: {p_value}")
# Si corr negativa i p < .05 vol dir que hi ha avituacio

# Treiem la trend
def remove_trend(row):
    x = np.arange(len(row))
    trend = np.polyval(np.polyfit(x, row, 1), x)  # Ajustar regresió lineal
    trend_demeaned = trend - np.mean(trend)  # Demean de la trend
    return row - trend_demeaned  # Remove trend

skin_trialbytrial_detrend = skin_trialbytrial.apply(remove_trend, axis=1)
# skin_trialbytrial_detrend.to_excel(join(basedir, 'SKIN_ARO_VAL', 'SCR_detrend.xlsx'))

ax = skin_trialbytrial_detrend.iloc[:,10:].T.plot(legend=False, figsize=(30,20))
ax.set_xticks(range(len(skin_trialbytrial_detrend.iloc[:,10:].columns)))
ax.set_xticklabels(skin_trialbytrial_detrend.iloc[:,10:].columns, rotation=45, ha='right', fontsize=18)
ax.tick_params(axis='y', labelsize=18)
ax.set_xlabel("Trials", fontsize=22)
ax.set_ylabel("Values", fontsize=22)
ax.set_title("Skin Conductance Trial by Trial", fontsize=26)
plt.grid(True)
plt.show()

fig, ax = plt.subplots(figsize=(20, 10))
ax.plot(mean_values.index[10:], mean_values.values[10:], color='b', linewidth=3, label='Mean')
ax.fill_between(mean_values.index[10:], q1.values[10:], q3.values[10:], color='b', alpha=0.15, label='IQR (Q1-Q3)')
# ax.plot(mean_values.index[10:], trend[10:], label="Trend (Regression)", linestyle="--", color="red")
ax.plot(mean_values.index[10:], skin_trialbytrial_detrend.iloc[:,10:].mean(axis=0), color='g', linewidth=3, label="Mean detrended")
ax.set_xticks(range(len(mean_values.index[10:])))
ax.set_xticklabels(mean_values.index[10:], rotation=45, ha='right', fontsize=14)
ax.set_xlabel("Trials", fontsize=18)
ax.set_ylabel("Values", fontsize=18)
ax.set_title("Skin Conductance (Median ± IQR)", fontsize=22)
ax.legend(fontsize=14)
plt.grid(True, linestyle="--", alpha=0.7)
plt.show()

conditions = ['Cond_CSplus_', 'Cond_Csminus_', 'REV_New_CSplus_', 'REV_New_CSminus_']   
skin_trialbytrial_NOdetrend = skin_trialbytrial
for cond in conditions:    
    skin_trialbytrial_NOdetrend[cond + 'mean'] = skin_trialbytrial_NOdetrend.loc[:, skin_trialbytrial_NOdetrend.columns.str.startswith(cond)].mean(axis=1)
    
    skin_trialbytrial_NOdetrend[cond + 'mean_early'] = skin_trialbytrial_NOdetrend.loc[:, [cond + 'trial1', cond + 'trial2', cond + 'trial3', 
                                                                                           cond + 'trial4', cond + 'trial5']].mean(axis=1)
    skin_trialbytrial_NOdetrend[cond + 'mean_late'] = skin_trialbytrial_NOdetrend.loc[:, [cond + 'trial6', cond + 'trial7', cond + 'trial8',
                                                                                          cond + 'trial9', cond + 'trial10']].mean(axis=1)
    
    skin_trialbytrial_detrend[cond + 'mean'] = skin_trialbytrial_detrend.loc[:, skin_trialbytrial_detrend.columns.str.startswith(cond)].mean(axis=1)
    
    skin_trialbytrial_detrend[cond + 'mean_early'] = skin_trialbytrial_detrend.loc[:, [cond + 'trial1', cond + 'trial2', cond + 'trial3', 
                                                                                       cond + 'trial4', cond + 'trial5']].mean(axis=1)
    skin_trialbytrial_detrend[cond + 'mean_late'] = skin_trialbytrial_detrend.loc[:, [cond + 'trial6', cond + 'trial7', cond + 'trial8',
                                                                                      cond + 'trial9', cond + 'trial10']].mean(axis=1)

# skin_used = skin_trialbytrial_NOdetrend.loc[:, skin_trialbytrial_NOdetrend.columns.str.contains('mean')]
skin_used = skin_trialbytrial_detrend.loc[:, skin_trialbytrial_detrend.columns.str.contains('mean')]

t_tests = [['Cond_CSplus_mean', 'Cond_Csminus_mean'], ['REV_New_CSplus_mean', 'REV_New_CSminus_mean'],
           ['Cond_CSplus_mean', 'REV_New_CSplus_mean'], ['Cond_Csminus_mean', 'REV_New_CSminus_mean']]

for test in t_tests:
    t, p = ttest_rel(skin_used.loc[:, test[0]], skin_used.loc[:, test[1]])
    print(test)
    print('T-statistic = ' + str(t) + '   p-value = ' + str(p) + '\n')

means_1 = skin_used.iloc[:,[0,3,6,9]].mean(axis=0, skipna=True)
errors_1 = within_subjects_sem(skin_used, skin_used.iloc[:,[0,3,6,9]].columns)

fig, ax = plt.subplots(1, 1, figsize=(12, 10))
ax.bar(means_1.index, means_1, yerr=errors_1, capsize=5, alpha=0.75, color=colors)
ax.set_ylabel('Mean SCR', fontsize=22)
ax.set_title('SKIN CONDUCTANCE RESPONSE', fontsize=22)
ax.set_xticklabels(leg, fontsize=20) # rotation=45, ha='right', rotation_mode='anchor'
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.tick_params(axis='y', labelsize=18)
ymax = means_1.max() + 0.011
ax.plot([0, 0, 1, 1], [ymax, ymax + 0.008, ymax + 0.008, ymax], lw=1.5, color='k')
ax.text(0.5, ymax + 0.01, "***", ha='center', fontsize=14) # bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
ax.plot([2, 2, 3, 3], [ymax, ymax + 0.008, ymax + 0.008, ymax], lw=1.5, color='k')
ax.text(2.5, ymax + 0.01, "***", ha='center', fontsize=14)
plt.show()

colors2 = ['#1f77b4', '#1c63c5', '#ffd307', '#ff9f07', '#aec7e8', '#acbcef', '#ffdf69', '#ffcb49']

means_2 = skin_used.iloc[:,[1,2,4,5,7,8,10,11]].mean(axis=0, skipna=True)
errors_2 = within_subjects_sem(skin_used, skin_used.iloc[:,[1,2,4,5,7,8,10,11]].columns)

fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.bar(means_2.index, means_2, yerr=errors_2, capsize=5, alpha=0.75, color=colors2)
ax.set_ylabel('mean_value', fontsize=22)
ax.set_title('SKIN CONDUCTANCE', fontsize=22)
ax.set_xticklabels(means_2.index, rotation=45, ha='right', rotation_mode='anchor', fontsize=16)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.tick_params(axis='y', labelsize=18)
plt.show()

#%%###################################### PATTERN EXPRESSION #########################################

### ATTENTION -- FALTA EL COSINE SIMILARITY!!!
means_pe = patexp.mean(axis=0, skipna=True)
# errors_pe = patexp.apply(lambda x: sem(x, nan_policy='omit'), axis=0)
errors_pe_1 = within_subjects_sem(patexp, patexp.iloc[:,[0,1,8,9]].columns)
errors_pe_2 = within_subjects_sem(patexp, patexp.iloc[:,[4,5,6,7,11,12,13,14]].columns)

fig, ax = plt.subplots(1, 1, figsize=(12, 10))
ax.bar(means_pe.iloc[[0,1,8,9]].index, means_pe.iloc[[0,1,8,9]], yerr=errors_pe_1, capsize=5, alpha=0.75, color=colors)
ax.set_ylabel('mean_value', fontsize=22)
ax.set_title('PATTERN EXPRESSION', fontsize=22)
ax.set_xticklabels(means_pe.iloc[[0,1,8,9]].index, rotation=45, ha='right', rotation_mode='anchor', fontsize=16)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.tick_params(axis='y', labelsize=18)
plt.show()

fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.bar(means_pe.iloc[[4,5,6,7,11,12,13,14]].index, means_pe.iloc[[4,5,6,7,11,12,13,14]], yerr=errors_pe_2, capsize=5, alpha=0.75, color=colors2)
ax.set_ylabel('mean_value', fontsize=22)
ax.set_title('PATTERN EXPRESSION', fontsize=22)
ax.set_xticklabels(means_pe.iloc[[4,5,6,7,11,12,13,14]].index, rotation=45, ha='right', rotation_mode='anchor', fontsize=16)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.tick_params(axis='y', labelsize=18)
plt.show()

#%%######################################### CORRELATIONS ############################################

import matplotlib.colors as mcolors
vmax = 0.054
bounds = np.linspace(0, vmax, 256)
cmap = plt.cm.YlOrBr
new_colors = cmap(np.linspace(0, 1, 256))
new_colors[-1] = [0, 0, 0, 1]  # RGBA para negro
custom_cmap = mcolors.ListedColormap(new_colors)
norm = mcolors.BoundaryNorm(bounds, custom_cmap.N)

# With Subjective Response (valence and arousal)
res_subjrat_c = pd.DataFrame(index=subj_rat.columns)
res_subjrat_p = pd.DataFrame(index=subj_rat.columns)

for pe in patexp.columns:
    for rate in subj_rat.columns:
        res_subjrat_c.loc[rate, pe] = pearsonr(patexp.loc[:, pe], subj_rat.loc[:, rate]).statistic
        res_subjrat_p.loc[rate, pe] = pearsonr(patexp.loc[:, pe], subj_rat.loc[:, rate]).pvalue

res_subjrat_c2 = res_subjrat_c.drop(['VITS_CS+CS-', 'VITS_diff', 'VITS_rev_diff'], axis=1)
res_subjrat_p2 = res_subjrat_p.drop(['VITS_CS+CS-', 'VITS_diff', 'VITS_rev_diff'], axis=1)

fig, axs = plt.subplots(2, 1, figsize=(25,30))  # Creates a 2x2 grid of subplots with a size of 10x10 inches
sns.set(font_scale=2)
sns.heatmap(res_subjrat_c2, ax=axs[0], cmap='coolwarm')
axs[0].set_title('Correlation coefficient', fontsize=35)
axs[0].tick_params(axis='both', labelsize=22)
axs[0].set_xticklabels(axs[0].get_xticklabels(), rotation=30, ha='right')
sns.heatmap(res_subjrat_p2, ax=axs[1], cmap=custom_cmap, norm=norm)
axs[1].set_title('p-value', fontsize=35)
axs[1].tick_params(axis='both', labelsize=22)
axs[1].set_xticklabels(axs[1].get_xticklabels(), rotation=30, ha='right')

res_subjrat_c.to_excel(join(basedir, 'SKIN_ARO_VAL', 'res_corr_pe_subjrating_valneg.xlsx'))
res_subjrat_p.to_excel(join(basedir, 'SKIN_ARO_VAL', 'res_pval_pe_subjrating_valneg.xlsx'))

# With Objective Response (skin conductance response)
res_scr_c = pd.DataFrame(index=skin_used.columns)
res_scr_p = pd.DataFrame(index=skin_used.columns)

for pe in patexp.columns:
    for scr in skin_used.columns:
        res_scr_c.loc[scr, pe] = pearsonr(patexp.loc[skin_used.index, pe], skin_used.loc[:, scr]).statistic
        res_scr_p.loc[scr, pe] = pearsonr(patexp.loc[skin_used.index, pe], skin_used.loc[:, scr]).pvalue

res_scr_c2 = res_scr_c.drop(['VITS_CS+CS-', 'VITS_diff', 'VITS_rev_diff'], axis=1)
res_scr_p2 = res_scr_p.drop(['VITS_CS+CS-', 'VITS_diff', 'VITS_rev_diff'], axis=1)

fig, axs = plt.subplots(2, 1, figsize=(25,30))  # Creates a 2x2 grid of subplots with a size of 10x10 inches
sns.set(font_scale=2)
sns.heatmap(res_scr_c2, ax=axs[0], cmap='coolwarm')
axs[0].set_title('Correlation coefficient', fontsize=35)
axs[0].tick_params(axis='both', labelsize=22)
axs[0].set_xticklabels(axs[0].get_xticklabels(), rotation=30, ha='right')
sns.heatmap(res_scr_p2, ax=axs[1], cmap=custom_cmap, norm=norm)
axs[1].set_title('p-value', fontsize=35)
axs[1].tick_params(axis='both', labelsize=22)
axs[1].set_xticklabels(axs[1].get_xticklabels(), rotation=30, ha='right')

res_scr_c.to_excel(join(basedir, 'SKIN_ARO_VAL', 'res_corr_pe_scr.xlsx'))
res_scr_p.to_excel(join(basedir, 'SKIN_ARO_VAL', 'res_pval_pe_scr.xlsx'))

# Between Subjective and Objective Response
shared_subjects = subj_rat.index.intersection(skin_used.index)
res_scr_subj_c = pd.DataFrame(index=skin_used.columns)
res_scr_subj_p = pd.DataFrame(index=skin_used.columns)

for rate in subj_rat.columns:
    for scr in skin_used.columns:
        res_scr_subj_c.loc[scr, rate] = pearsonr(subj_rat.loc[shared_subjects, rate], skin_used.loc[shared_subjects, scr]).statistic
        res_scr_subj_p.loc[scr, rate] = pearsonr(subj_rat.loc[shared_subjects, rate], skin_used.loc[shared_subjects, scr]).pvalue

fig, axs = plt.subplots(2, 1, figsize=(22,35))  # Creates a 2x2 grid of subplots with a size of 10x10 inches
sns.set(font_scale=2)
sns.heatmap(res_scr_subj_c, ax=axs[0], cmap='coolwarm')
axs[0].set_title('Correlation coefficient', fontsize=35)
axs[0].tick_params(axis='both', labelsize=22)
axs[0].set_xticklabels(axs[0].get_xticklabels(), rotation=25, ha='right')
sns.heatmap(res_scr_subj_p, ax=axs[1], cmap=custom_cmap, norm=norm)
axs[1].set_title('p-value', fontsize=35)
axs[1].tick_params(axis='both', labelsize=22)
axs[1].set_xticklabels(axs[1].get_xticklabels(), rotation=25, ha='right')

res_scr_subj_c.to_excel(join(basedir, 'SKIN_ARO_VAL', 'res_corr_subjrating_scr.xlsx'))
res_scr_subj_p.to_excel(join(basedir, 'SKIN_ARO_VAL', 'res_pval_subjrating_scr.xlsx'))

#%%######################################## ANXIETY -- SCR ###########################################

# Relation between anxiety (DASS, SCSR-P, PC1-withoutEMA) and SCR
dass_a = pd.read_excel(join(basedir, 'Mult_log_regression', 'DASS_A_A_patexp.xlsx'), index_col=0)
dass_a.index = dass_a.index.str.replace('sub-', '', regex=True)
dass_d = pd.read_excel(join(basedir, 'Mult_log_regression', 'DASS_D_A_patexp.xlsx'), index_col=0)
dass_d.index = dass_d.index.str.replace('sub-', '', regex=True)
dass_s = pd.read_excel(join(basedir, 'Mult_log_regression', 'DASS_S_A_patexp.xlsx'), index_col=0)
dass_s.index = dass_s.index.str.replace('sub-', '', regex=True)
scsr_p = pd.read_excel(join(basedir, 'Mult_log_regression', 'SCSR_P_A_patexp.xlsx'), index_col=0)
scsr_p.index = scsr_p.index.str.replace('sub-', '', regex=True)
pca = pd.read_excel(join(basedir, 'Mult_log_regression', 'pca_without_EMA_tertil_patexp.xlsx'), index_col=0)
pca.index = pca.index.str.replace('sub-', '', regex=True)

anx_tertils = pd.DataFrame(index=sorted(list(set().union(*[df.index for df in [dass_a, dass_d, dass_s, scsr_p, pca]]))), 
                           columns=['DASS_A_low', 'DASS_D_low', 'DASS_S_low', 'SCSR_P_low', 'PCA1_low',
                                    'DASS_A_high', 'DASS_D_high', 'DASS_S_high', 'SCSR_P_high', 'PCA1_high'])

anx_tertils.DASS_A_low[dass_a[dass_a.IQ==-1].index] = 1
anx_tertils.DASS_A_high[dass_a[dass_a.IQ==1].index] = 1
anx_tertils.DASS_D_low[dass_d[dass_d.IQ==-1].index] = 1
anx_tertils.DASS_D_high[dass_d[dass_d.IQ==1].index] = 1
anx_tertils.DASS_S_low[dass_s[dass_s.IQ==-1].index] = 1
anx_tertils.DASS_S_high[dass_s[dass_s.IQ==1].index] = 1
anx_tertils.SCSR_P_low[scsr_p[scsr_p.IQ==-1].index] = 1
anx_tertils.SCSR_P_high[scsr_p[scsr_p.IQ==1].index] = 1
anx_tertils.PCA1_low[pca[pca.IQ==-1].index] = 1
anx_tertils.PCA1_high[pca[pca.IQ==1].index] = 1
anx_tertils = anx_tertils.fillna(0)

low_high_counts = pd.DataFrame({'low': anx_tertils.filter(like='_low').sum(axis=1), 
                                'high': anx_tertils.filter(like='_high').sum(axis=1)})

colors_anx = ["#ffffff", # Blanco = 0
              "#ccffcc",  # Verde más claro = 1
              "#66cc66",  # Verde claro = 2
              "#00a000",  # Verde medio = 3
              "#007500",  # Verde oscuro medio = 4
              "#004d00",  # Verde más intenso = 5
              "#ff0000",  # Rojo intenso = 6
              "#ff5500",  # Rojo claro = 7
              "#ffaa00",  # Naranja = 8
              "#ffff00"]  # Amarillo = 9

good = [0, 1, 2, 3, 4, 5]
bad = [0, 6, 7, 8, 9]  # Amarillo = 4

for subj, row in low_high_counts.iterrows():
    # if subj == 'AXC007':
    #     f
    if any(row == 0):
        # AQUEST SERIA EL COLOR DOLENT = blanc
        low_high_counts.loc[subj, row[row == 0].index + '_color'] = good[0]
        # AQUEST SERIA EL COLOR BO = escala de verds
        low_high_counts.loc[subj, row[row != 0].index + '_color'] = good[row[row != 0].values[0]]

    elif any(row == 1):
        # AQUEST SERIA EL COLOR DOLENT
        if all(row == 1):
            low_high_counts.loc[subj, 'low_color'] = bad[1]
            low_high_counts.loc[subj, 'high_color'] = bad[1]
        else:
            low_high_counts.loc[subj, row[row == 1].index + '_color'] = bad[row[row != 1].values[0]]
            # AQUEST SERIA EL COLOR BO
            if any(row > 2):
                low_high_counts.loc[subj, row[row != 1].index + '_color'] = good[int(row.diff()[1])]
            else:
                low_high_counts.loc[subj, row[row != 1].index + '_color'] = bad[row[row != 1].values[0]]
            # algun de l'escala de vermell/groc + verd en funcio de l'altre en 4 i 3 -- podem restar i aixi no es tan fosc je je
    else:
        if any(row == 3):
            low_high_counts.loc[subj, 'low_color'] = bad[2]
            low_high_counts.loc[subj, 'high_color'] = bad[2]
        else:
            low_high_counts.loc[subj, 'low_color'] = bad[1]
            low_high_counts.loc[subj, 'high_color'] = bad[1]

anx_colors = pd.DataFrame([low_high_counts.iloc[:,-2], low_high_counts.iloc[:,-2], low_high_counts.iloc[:,-2], low_high_counts.iloc[:,-2], low_high_counts.iloc[:,-2],
                           low_high_counts.iloc[:,-1], low_high_counts.iloc[:,-1], low_high_counts.iloc[:,-1], low_high_counts.iloc[:,-1], low_high_counts.iloc[:,-1]]).T
anx_colors.columns = anx_tertils.columns
heatmap_data = anx_tertils.astype(int) * anx_colors.astype(int)

plt.figure(figsize=(20, 3))
sns.heatmap(heatmap_data.T, cmap=colors_anx, cbar=False, linewidths=0.5)
plt.xlabel("Subjects")
plt.ylabel("Variables & Tertiles")
plt.title("Shared Subjects Across Variables & Tertiles")
plt.show()

# Mirem per separat cada constructe amb la SCR
anx_tertils_withSCR = anx_tertils.loc[anx_tertils.index.intersection(skin_used.index),:]

for q in range(5):
    q_low = anx_tertils_withSCR.columns[q]
    q_high = anx_tertils_withSCR.columns[q+5]
    q_name = q_low.replace('_low', '').replace('_', '-')
    
    scr_quest1_inf = skin_used.loc[anx_tertils_withSCR[anx_tertils_withSCR[q_low] == 1].index, 
                                   ['Cond_CSplus_mean', 'Cond_Csminus_mean', 'REV_New_CSplus_mean', 'REV_New_CSminus_mean']]
    scr_quest1_sup = skin_used.loc[anx_tertils_withSCR[anx_tertils_withSCR[q_high] == 1].index, 
                                   ['Cond_CSplus_mean', 'Cond_Csminus_mean', 'REV_New_CSplus_mean', 'REV_New_CSminus_mean']]
    
    scr_quest2_inf = skin_used.loc[anx_tertils_withSCR[anx_tertils_withSCR[q_low] == 1].index, 
                                   ['Cond_CSplus_mean_early', 'Cond_CSplus_mean_late', 'Cond_Csminus_mean_early', 'Cond_Csminus_mean_late', 
                                    'REV_New_CSplus_mean_early', 'REV_New_CSplus_mean_late', 'REV_New_CSminus_mean_early', 'REV_New_CSminus_mean_late']]
    
    scr_quest2_sup = skin_used.loc[anx_tertils_withSCR[anx_tertils_withSCR[q_high] == 1].index, 
                                   ['Cond_CSplus_mean_early', 'Cond_CSplus_mean_late', 'Cond_Csminus_mean_early', 'Cond_Csminus_mean_late', 
                                    'REV_New_CSplus_mean_early', 'REV_New_CSplus_mean_late', 'REV_New_CSminus_mean_early', 'REV_New_CSminus_mean_late']]
    
    
    means_scr_quest1_inf = scr_quest1_inf.mean(axis=0, skipna=True)
    errors_scr_quest1_inf = within_subjects_sem(scr_quest1_inf, scr_quest1_inf.columns)
    means_scr_quest1_sup = scr_quest1_sup.mean(axis=0, skipna=True)
    errors_scr_quest1_sup = within_subjects_sem(scr_quest1_sup, scr_quest1_sup.columns)
    
    x = np.arange(len(means_scr_quest1_inf))  # Posiciones en el eje X
    width = 0.45  # Ancho de las barras
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    bars1 = ax.bar(x - width/2, means_scr_quest1_inf, width, yerr=errors_scr_quest1_inf, 
                   capsize=5, alpha=0.75, color=colors, label='Inferior Tertil')
    bars2 = ax.bar(x + width/2, means_scr_quest1_sup, width, yerr=errors_scr_quest1_sup, 
                   capsize=5, alpha=0.75, color=colors, hatch='//', label='Superior Tertil')
    ax.set_xticks(x)
    ax.set_xticklabels(means_scr_quest1_inf.index, rotation=45, ha='right', fontsize=16)
    ax.set_ylabel('mean_value', fontsize=22)
    ax.set_title('SKIN CONDUCTANCE - ' + q_name + ' TERTILES', fontsize=22)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.tick_params(axis='y', labelsize=18)
    ax.legend(fontsize=18)
    plt.show()
    
    colors2 = ['#1f77b4', '#1c63c5', '#ffd307', '#ff9f07', '#aec7e8', '#acbcef', '#ffdf69', '#ffcb49']
    
    means_scr_quest2_inf = scr_quest2_inf.mean(axis=0, skipna=True)
    errors_scr_quest2_inf = within_subjects_sem(scr_quest2_inf, scr_quest2_inf.columns)
    means_scr_quest2_sup = scr_quest2_sup.mean(axis=0, skipna=True)
    errors_scr_quest2_sup = within_subjects_sem(scr_quest2_sup, scr_quest2_sup.columns)
    
    x = np.arange(len(means_scr_quest2_inf))  # Posiciones en el eje X
    width = 0.45  # Ancho de las barras
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    bars1 = ax.bar(x - width/2, means_scr_quest2_inf, width, yerr=errors_scr_quest2_inf, 
                   capsize=5, alpha=0.75, color=colors, label='Inferior Tertil')
    bars2 = ax.bar(x + width/2, means_scr_quest2_sup, width, yerr=errors_scr_quest2_sup, 
                   capsize=5, alpha=0.75, color=colors, hatch='//', label='Superior Tertil')
    ax.set_xticks(x)
    ax.set_xticklabels(means_scr_quest2_inf.index, rotation=45, ha='right', fontsize=16)
    ax.set_ylabel('mean_value', fontsize=22)
    ax.set_title('SKIN CONDUCTANCE - ' + q_name + ' TERTILES', fontsize=22)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.tick_params(axis='y', labelsize=18)
    ax.legend(fontsize=18)
    plt.show()
    
    
    ######## REVISAR QUE TINGUI SENTIT EL QUE ESTEM FENT ---- FER ALGUNA COMPROVACIÓ!!!
    
