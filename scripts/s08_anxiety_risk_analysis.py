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
import seaborn as sns
from scipy.stats import ttest_ind, pearsonr
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

subbase = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git'
basedir = join(subbase, 'results', 'final_brainmask')
savedir = join(basedir, 'Mult_log_regression', 'PATTERN_EXPRESSION_xval')

path_exc = join(basedir, '2_SVM_results_stai') #all_sig_patexp

patexp = pd.read_excel(join(path_exc, 'pat_exp_all_data_xval_10fold.xlsx'), index_col=0)
var = pd.read_excel(join(subbase, 'FIS_AX_per_Angels_27_06_25_puntuacions_totals.xlsx'), index_col=0).add_prefix("sub-", axis=0)

# patexp.columns = patexp.columns.str.replace('Our_sig', 'VITS')
# patexp_used_1 = patexp.filter(like="VITS")
patexp_used_1 = patexp

#%% PCA
var_used = ['STAI_T_A', 'SCSR_P_A']

data_used = var.loc[:, var_used]
data_used = data_used.dropna()
data_used = data_used.loc[patexp_used_1.index,:]
col_name = 'anxiety_risk'

# Data normalization
res_pca = pd.DataFrame(index=patexp_used_1.index)

scaler = StandardScaler()
data_scaled = pd.DataFrame(data=scaler.fit_transform(data_used), columns=data_used.columns, index=data_used.index)

pca95 = PCA(n_components=0.95)
pca = pca95.fit_transform(data_scaled)
df_pca = pd.DataFrame(pca[:,0], index=data_used.index, columns=['anxiety_risk'])
res_pca = res_pca.merge(df_pca, left_index=True, right_index=True, how='left')

# explained_variance_ratio_ = how much variance of the total data is explained by each principal component 
plt.figure(figsize=(8, 5))
plt.bar(range(1, pca.shape[1]+1), pca95.explained_variance_ratio_, alpha=0.5, align='center', label='individual explained variance')
plt.step(range(1, pca.shape[1]+1), pca95.explained_variance_ratio_.cumsum(), where='mid', label='cumulative explained variance')
# plt.axhline(y=0.95, color='r', linestyle='-')
# plt.axhline(y=0.8, color='r', linestyle='-')
for i, value in enumerate(pca95.explained_variance_ratio_):
    plt.text(i + 1, value + 0.01, f"{value:.2f}", ha='center', fontsize=16)  # Ajusta el desplazamiento con `value + 0.01`
plt.ylabel('Explained variance ratio', fontsize=19)
plt.xlabel('Principal components', fontsize=19)
plt.title(col_name, fontsize=19)
plt.title('Explained variance', fontsize=20)
plt.legend(loc='best', fontsize=16)
plt.xticks(fontsize=17)
plt.yticks(fontsize=17)
plt.show()

# Histogram (contribution of each original variable to PC1)
plt.figure(figsize=(8, 5))
plt.bar(list(data_used.columns), pca95.components_[0])
plt.xlabel('Original features', fontsize=19)
plt.ylabel('Contribution', fontsize=18)
plt.title('Contribution of original features to PC1 ' + col_name, fontsize=19)
plt.title('Contribution of original features to PC1', fontsize=19)
new_labels = ['DASS-S', 'DASS-A', 'DASS-D', 'STAI-T', 'SPSR-P']
plt.xticks(ticks=range(len(new_labels)), labels=new_labels, fontsize=17)
plt.yticks(fontsize=17)
plt.show()


sns.distplot(pca[:,0])
plt.xlabel('PC1 value')
plt.ylabel('Number of Cases')
plt.title('Distribution of PC1 ' + col_name + ' N = ' + str(data_scaled.shape[0]))
plt.show()
    
res_pca.to_excel(join(savedir, 'pc1_anxiety_risk.xlsx'))

###
res_pca = pd.read_excel(join(basedir,'Mult_log_regression', 'PATTERN_EXPRESSION_xval', 'pc1_anxiety_risk.xlsx'), index_col=0)
col_name = 'anxiety_risk'

patexp_used = patexp_used_1.merge(var[['Age_A','Sex']], left_index=True, right_index=True).merge(res_pca[col_name], left_index=True, right_index=True)
patexp_used = patexp_used.dropna()
# patexp_used.to_excel(join(savedir, col_name + '_all_patexp.xlsx'))

# Check continuos correlation (pearson correlation) ---- revisar això, crec que es la correlacio lineal amb tota la mostra que fem
pearsonr(patexp_used[col_name], patexp_used['VITCS_CS+'])
pearsonr(patexp_used[col_name], patexp_used['VITCS_CS-'])

# Tertils
patexp_used['IQ'] = np.zeros(patexp_used.shape[0])
n_iq = round(patexp_used.shape[0]/3)
iq = np.quantile(patexp_used[col_name], [1/3, 2/3])

# Inferior tertil
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

# Superior tertil
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

summary = patexp_used.groupby('IQ_label')[col_name].agg(['mean', 'std', 'count'])
summary['sem'] = summary['std'] / np.sqrt(summary['count'])  # error estàndard de la mitjana
summary = summary.reindex(['Low tertile', 'High tertile'])

plt.figure(figsize=(5,4))
plt.bar(summary.index, summary['mean'], yerr=summary['sem'], color=["#2B6CB0", "#E76F51"],
    capsize=8, edgecolor='black', alpha=0.8)
plt.ylabel('Mean PC1', fontsize=18)
plt.xlabel('Group', fontsize=18)
plt.title('PC1 by tertile group', fontsize=19)
plt.xticks(fontsize=17)
plt.yticks(fontsize=17)
plt.tight_layout()
plt.show()

for pe in patexp_used.columns[:2]:
    summary = patexp_used.groupby('IQ_label')[pe].agg(['mean', 'std', 'count'])
    summary['sem'] = summary['std'] / np.sqrt(summary['count'])  # error estàndard de la mitjana
    summary = summary.reindex(['Low tertile', 'High tertile'])
    
    stat, p = ttest_ind(patexp_used[patexp_used['IQ_label'] == 'Low tertile'][pe].dropna(), 
                        patexp_used[patexp_used['IQ_label'] == 'High tertile'][pe].dropna(), equal_var=False)
    import pingouin as pg
    d = pg.compute_effsize(patexp_used[patexp_used['IQ_label'] == 'Low tertile'][pe].dropna(), 
                        patexp_used[patexp_used['IQ_label'] == 'High tertile'][pe].dropna(), eftype='cohen')
    print(pe)
    print('T = ' + str(stat) + ' / p = ' + str(p) + ' / d = ' + str(d))
    plt.figure(figsize=(2.6,2))
    plt.bar(summary.index, summary['mean'], yerr=summary['sem'], color=["#2B6CB0", "#E76F51"],
        capsize=8, edgecolor='black', alpha=0.8)
    x1, x2 = 0, 1
    y = (summary['mean'].max() + summary['sem'].max())* 1.03
    h = y * 0.1  # altura de la línea
    plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c='k')
    if p <= 0.001: text = "***"
    elif p <= 0.01: text = "** T=2.83, d=0.53"
    elif p <= 0.05: text = "* T=2.07, d=0.39"
    elif p <= 0.1: text = "p=" + str(round(p, 2))
    else: text = "ns"
    plt.text((x1 + x2) * 0.5, (y + h)* 1.05, text, ha='center', fontsize=9)
    plt.ylim(top = (y + h)*1.25)
    plt.ylabel(f'Mean {pe}', fontsize=13)
    # plt.xlabel('Group', fontsize=13)
    # plt.title('PC1 low-high tertiles', fontsize=19)
    plt.xticks([0, 1], ["Low\ntertile", "High\ntertile"], fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    # plt.savefig(join(savedir, 'pat_exp_distributions_final_PCA1_' + pe + '.png'))
    plt.show()
    
print('IQ = -1: ' + str(sum(patexp_used.IQ == -1)) + '; IQ = 1: ' + str(sum(patexp_used.IQ == 1)))

patexp_used.to_excel(join(savedir, col_name + '_patexp_tertils.xlsx'))



