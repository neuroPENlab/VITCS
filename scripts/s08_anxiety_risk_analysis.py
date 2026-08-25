#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s08_anxiety_risk_analysis.py
@author: Angels Calvet-Mirabent

Test whether VITCS pattern expression differs between individuals at high vs. low risk for anxiety, 
using a composite anxiety-risk score.

From Methods: "To derive a composite index of anxiety risk, scores from the STAI-T and the SPSRQ-P were 
first standardized and then subjected to principal component analysis (PCA). The first principal component 
captured shared variance between the two measures (80%) and was used as a composite anxiety-risk score. 
Participants were subsequently divided into upper (high-risk; n = 57) and lower (low-risk; n = 57) 
tertiles based on this composite score. VITCS pattern expression values were computed as the dot product 
between the VITCS weight map and individual whole-brain activation maps for CS+ and CS- trials."

Run once per signature: set SIGNATURE below and re-run.
"""
import os
from os.path import join
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, pearsonr
import pingouin as pg
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- User-defined paths (TO EDIT) -------------------------------------------
basedir = '<PATH_TO_PROJECT>'  # <-- EDIT THIS, same as other scripts
datadir = join(basedir, 'data')

questionnaire_path = '<PATH_TO_QUESTIONNAIRE_SCORES>'    # <-- EDIT THIS: table with STAI_T_A and SCSR_P_A columns per participant

# ---  Which signature to run mediation for ----------------------------------
SIGNATURE = "VITCS" # <-- EDIT THIS: 'VITCS' | 'Reddan_Threat' | 'Liu_SUITAS' | 'VITCS_early' | 'VITCS_late'

if SIGNATURE == "VITCS":
    pat_exp_path = join(basedir, 'results', 'VITCS_development', 'pat_exp_full_sample_xval.xlsx'); # from 04b + 04d
    pat_exp_col = ['CS+', 'CS-'];
    savedir = join(basedir, 'results', 'VITCS_anxiety_risk');
elif SIGNATURE == "Reddan_Threat":
    pat_exp_path = join(basedir, 'results', 'VITCS_development', 'pat_exp_full_sample_all_signatures.xlsx'); # from 04d
    pat_exp_col = ['Reddan_Threat_CS+', 'Reddan_Threat_CS-'];
    savedir = join(basedir, 'results', 'comparison_existing_signatures');
elif SIGNATURE == "Liu_SUITAS":
    pat_exp_path = join(basedir, 'results', 'VITCS_development', 'pat_exp_full_sample_all_signatures.xlsx'); # from 04d
    pat_exp_col = ['Liu_SUITAS_CS+', 'Liu_SUITAS_CS-'];
    savedir = join(basedir, 'results', 'comparison_existing_signatures');
elif SIGNATURE == "VITCS_early":
    pat_exp_path = join(basedir, 'results', 'VITCS_early_results', 'pat_exp_full_sample_xval.xlsx'); # from 04c
    pat_exp_col = ['CS+', 'CS-'];
    savedir = join(basedir, 'results', 'VITCS_early_results');
elif SIGNATURE == "VITCS_late":
    pat_exp_path = join(basedir, 'results', 'VITCS_late_results', 'pat_exp_full_sample_xval.xlsx'); # from 04c
    pat_exp_col = ['CS+', 'CS-'];
    savedir = join(basedir, 'results', 'VITCS_late_results');
else:
    print("That's not a valid signature.")

os.makedirs(savedir, exist_ok=True)

#%% Load data -------------------------------------------------------------------
patexp = pd.read_excel(pat_exp_path, index_col=0)
var = pd.read_excel(questionnaire_path, index_col=0).add_prefix("sub-", axis=0)

#%% PCA: composite anxiety-risk score (STAI-T + SPSRQ-P) -------------------------
var_used = ['STAI_T_A', 'SCSR_P_A']
col_name = 'anxiety_risk'

if not os.path.exists(join(datadir, 'pc1_anxiety_risk.xlsx')):
    data_used = var.loc[:, var_used]
    data_used = data_used.dropna()
    data_used = data_used.loc[patexp.index, :]
    
    # Data normalization
    scaler = StandardScaler()
    data_scaled = pd.DataFrame(data=scaler.fit_transform(data_used), columns=data_used.columns, index=data_used.index)
    
    # Define PCA
    pca95 = PCA(n_components=0.95)
    pca = pca95.fit_transform(data_scaled)
    
    res_pca = pd.DataFrame(pca[:, 0], index=data_used.index, columns=[col_name])
    
    # Explained variance
    plt.figure(figsize=(8, 5))
    plt.bar(range(1, pca.shape[1] + 1), pca95.explained_variance_ratio_, alpha=0.5, align='center', label='individual explained variance')
    plt.step(range(1, pca.shape[1] + 1), pca95.explained_variance_ratio_.cumsum(), where='mid', label='cumulative explained variance')
    for i, value in enumerate(pca95.explained_variance_ratio_):
        plt.text(i + 1, value + 0.01, f"{value:.2f}", ha='center', fontsize=16)
    plt.ylabel('Explained variance ratio', fontsize=19)
    plt.xlabel('Principal components', fontsize=19)
    plt.title('Explained variance', fontsize=20)
    plt.legend(loc='best', fontsize=16)
    plt.xticks(fontsize=17)
    plt.yticks(fontsize=17)
    plt.show()
    
    # Contribution of each original variable to PC1
    plt.figure(figsize=(8, 5))
    plt.bar(list(data_used.columns), pca95.components_[0])
    plt.xlabel('Original features', fontsize=19)
    plt.ylabel('Contribution', fontsize=18)
    plt.title('Contribution of original features to PC1', fontsize=19)
    new_labels = ['STAI-T', 'SPSRQ-P']
    plt.xticks(ticks=range(len(new_labels)), labels=new_labels, fontsize=17)
    plt.yticks(fontsize=17)
    plt.show()
    
    # Principal component 1 (PC1) distribution
    sns.distplot(pca[:, 0])
    plt.xlabel('PC1 value')
    plt.ylabel('Number of Cases')
    plt.title(f'Distribution of PC1 {col_name}, N = {data_scaled.shape[0]}')
    plt.show()
    
    # Save result
    res_pca.to_excel(join(datadir, 'pc1_anxiety_risk.xlsx'))

else:
    res_pca = pd.read_excel(join(datadir, 'pc1_anxiety_risk.xlsx'), index_col=0)

#%% Merge PC1 anxiety-risk score with pattern expression --------------------------
patexp_used = patexp.merge(var[['Age_A', 'Sex']], left_index=True, right_index=True).merge(res_pca[col_name], left_index=True, right_index=True)
patexp_used = patexp_used.dropna()
patexp_used.to_excel(join(savedir, col_name + '_patexp.xlsx'))

# Sanity check: continuous correlation between anxiety-risk score and VITCS pattern expression
r_csplus = pearsonr(patexp_used[col_name], patexp_used[pat_exp_col[0]])
r_csminus = pearsonr(patexp_used[col_name], patexp_used[pat_exp_col[1]])
print(f"anxiety_risk vs VITCS_CS+: r={r_csplus[0]:.3f}, p={r_csplus[1]:.4f}")
print(f"anxiety_risk vs VITCS_CS-: r={r_csminus[0]:.3f}, p={r_csminus[1]:.4f}")

#%% Split into upper/lower tertiles (high-risk n=57, low-risk n=57) ----------------
patexp_used['IQ'] = np.zeros(patexp_used.shape[0])
n_iq = round(patexp_used.shape[0]/3)
iq = np.quantile(patexp_used[col_name], [1/3, 2/3])

# Lower tertile
if sum(patexp_used[col_name] < iq[0]) < n_iq:
    n_add = n_iq - sum(patexp_used[col_name] < iq[0])
    selected_indices = patexp_used[col_name] < iq[0]
    selected_indices[patexp_used[patexp_used[col_name] == iq[0]].sample(n=n_add, random_state=42).index] = True
elif sum(patexp_used[col_name] < iq[0]) > n_iq:
    n_sub = sum(patexp_used[col_name] < iq[0]) - n_iq
    selected_indices = patexp_used[col_name] < iq[0]
    selected_indices[patexp_used[patexp_used[col_name] == patexp_used[patexp_used[col_name] < iq[0]][col_name].max()].sample(n=n_sub, random_state=42).index] = False
else:
    selected_indices = patexp_used[col_name] < iq[0]
patexp_used.loc[selected_indices, 'IQ'] = -1

# Upper tertile
if sum(patexp_used[col_name] > iq[1]) < n_iq:
    n_add = n_iq - sum(patexp_used[col_name] > iq[1])
    selected_indices = patexp_used[col_name] > iq[1]
    selected_indices[patexp_used[patexp_used[col_name] == iq[1]].sample(n=n_add, random_state=42).index] = True
elif sum(patexp_used[col_name] > iq[1]) > n_iq:
    n_sub = sum(patexp_used[col_name] > iq[1]) - n_iq
    selected_indices = patexp_used[col_name] > iq[1]
    selected_indices[patexp_used[patexp_used[col_name] == patexp_used[patexp_used[col_name] > iq[1]][col_name].min()].sample(n=n_sub, random_state=42).index] = False
else:
    selected_indices = patexp_used[col_name] > iq[1]
patexp_used.loc[selected_indices, 'IQ'] = 1

patexp_used = patexp_used.drop(patexp_used[patexp_used['IQ'] == 0].index)
patexp_used['IQ_label'] = patexp_used['IQ'].map({-1: 'Low tertile', 1: 'High tertile'})

print('Low-risk tertile: n = ' + str(sum(patexp_used.IQ == -1)) + '; High-risk tertile: n = ' + str(sum(patexp_used.IQ == 1)))

#%% PC1 by tertile group (sanity-check plot) ---------------------------------------
summary = patexp_used.groupby('IQ_label')[col_name].agg(['mean', 'std', 'count'])
summary['sem'] = summary['std'] / np.sqrt(summary['count'])
summary = summary.reindex(['Low tertile', 'High tertile'])

plt.figure(figsize=(5, 4))
plt.bar(summary.index, summary['mean'], yerr=summary['sem'], color=["#2B6CB0", "#E76F51"],
        capsize=8, edgecolor='black', alpha=0.8)
plt.ylabel('Mean PC1', fontsize=18)
plt.xlabel('Group', fontsize=18)
plt.title('PC1 by tertile group', fontsize=19)
plt.xticks(fontsize=17)
plt.yticks(fontsize=17)
plt.tight_layout()
plt.show()

#%% Group differences in VITCS pattern expression (CS+, CS-) between tertiles ------
for pe in pat_exp_col:
    low = patexp_used[patexp_used['IQ_label'] == 'Low tertile'][pe].dropna()
    high = patexp_used[patexp_used['IQ_label'] == 'High tertile'][pe].dropna()

    stat, p = ttest_ind(low, high, equal_var=False)
    d = pg.compute_effsize(low, high, eftype='cohen')
    print(pe)
    print('T = ' + str(stat) + ' / p = ' + str(p) + ' / d = ' + str(d))

    summary = patexp_used.groupby('IQ_label')[pe].agg(['mean', 'std', 'count'])
    summary['sem'] = summary['std'] / np.sqrt(summary['count'])
    summary = summary.reindex(['Low tertile', 'High tertile'])

    plt.figure(figsize=(2.6, 2))
    plt.bar(summary.index, summary['mean'], yerr=summary['sem'], color=["#2B6CB0", "#E76F51"],
            capsize=8, edgecolor='black', alpha=0.8)
    x1, x2 = 0, 1
    y = (summary['mean'].max() + summary['sem'].max()) * 1.03
    h = y * 0.1
    plt.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, c='k')
    if p <= 0.001: text = "***"
    elif p <= 0.01: text = "**"
    elif p <= 0.05: text = "*"
    elif p <= 0.1: text = "p=" + str(round(p, 2))
    else: text = "ns"
    plt.text((x1 + x2) * 0.5, (y + h) * 1.05, text, ha='center', fontsize=9)
    plt.ylim(top=(y + h) * 1.25)
    plt.ylabel(f'Mean {pe}', fontsize=13)
    plt.xticks([0, 1], ["Low\ntertile", "High\ntertile"], fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.show()

patexp_used.to_excel(join(savedir, col_name + '_patexp_tertils.xlsx'))
