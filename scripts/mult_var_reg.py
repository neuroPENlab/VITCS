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
from statannotations.Annotator import Annotator
from scipy.stats import ttest_ind, pearsonr

subbase = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git'
basedir = join(subbase, 'results', 'final_brainmask')
savedir = join(basedir, 'Mult_log_regression', 'PATTERN_EXPRESSION_xval')

# savedir = join(basedir, 'Mult_log_regression_long')

# path_exc = join(basedir, '3_sig_evaluation_test', 'results_new_CS+CS-diff') #all_sig_patexp
# path_exc = join(basedir, '2_SVM_results_stai') #all_sig_patexp
path_exc = join(basedir, '1_sig_evaluation') #all_sig_patexp
#path_exc = join(basedir, '2_SVM_results_stai') #all_sig_patexp

# patexp = pd.read_excel(join(path_exc, 'pat_exp_all_data_xval_10fold.xlsx'), index_col=0)
patexp = pd.read_excel(join(path_exc, 'pat_exp_reddan.xlsx'), index_col=0)
# patexp = pd.read_excel(join(path_exc, 'pat_exp_all_data_xval_new.xlsx'), index_col=0) # pat_exp_all_data_xval
var = pd.read_excel(join(subbase, 'Quest_final_dataset.xlsx'), index_col=0).add_prefix("sub-", axis=0)
var = pd.read_excel(join(subbase, 'FIS_AX_per_Angels_27_06_25_puntuacions_totals.xlsx'), index_col=0).add_prefix("sub-", axis=0)

# patexp.columns = patexp.columns.str.replace('Our_sig', 'VITS')
# patexp_used_1 = patexp.filter(like="VITS")
patexp_used_1 = patexp

scr = pd.read_excel(join(basedir, 'SKIN_ARO_VAL', 'SCR_detrend.xlsx'), index_col=0).add_prefix("sub-", axis=0)
scr_used_1 = scr.loc[:,scr.columns.str.contains('mean')]

subj_rat = pd.read_excel(join(basedir, 'SKIN_ARO_VAL', 'Subjective_ratings_condrev.xlsx'), index_col=0).add_prefix("sub-", axis=0)

#%% BASELINE

var_corr = [['DASS_S_A'], ['DASS_A_A'], ['DASS_D_A'], ['STAI_T_A'], ['SCSR_P_A']] #, ['EMA_2weeks_first']
var_corr_name = ['DASS-S', 'DASS-A', 'DASS-D', 'STAI-T', 'SPSR-P']
var_corr = [['PSWQ_T_A'], ['ASI_AxTA'], ['IoUS_T_A'], ['LSAS_T_A'], ['TAG_T_A']] #, ['EMA_2weeks_first'] NEWWWWW
var_corr = [['DASS_S_A'], ['DASS_A_A'], ['DASS_D_A'], ['STAI_T_A'], ['SCSR_P_A'], ['PSWQ_T_A'], ['ASI_AxTA'], ['IoUS_T_A'], ['LSAS_T_A'], ['TAG_T_A']]
exc_idx = ['DASS', 'OTH'] #, 'EMA'

#%%########################################## PE #############################################
#for qq, e in zip(var_corr, exc_idx):    
tval = pd.DataFrame(index=['CS+', 'CS-', 'CS+>CS-', 'CS+early', 'CS+late', 'CS-early', 'CS-late', 'CS+rev', 'CS-rev', 
                           'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'], 
                    columns=['DASS_S_A', 'DASS_A_A', 'DASS_D_A', 'STAI_T_A', 'SCSR_P_A'])
pval = pd.DataFrame(index=['CS+', 'CS-', 'CS+>CS-', 'CS+early', 'CS+late', 'CS-early', 'CS-late', 'CS+rev', 'CS-rev', 
                           'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'], 
                    columns=['DASS_S_A', 'DASS_A_A', 'DASS_D_A', 'STAI_T_A', 'SCSR_P_A'])
for n, q in enumerate(var_corr):
    
    #for qq in q:
    qq = q[0]
    patexp_used = patexp_used_1.merge(var[['Age_A','Sex'] + q], left_index=True, right_index=True)
    patexp_used = patexp_used.dropna()
    # patexp_used.to_excel(join(savedir, e + '_patexp.xlsx'))
    
    patexp_used['IQ'] = np.zeros(patexp_used.shape[0])
    patexp_used['IQ2'] = np.zeros(patexp_used.shape[0])
    n_iq = round(patexp_used.shape[0]/3)
    iq = np.quantile(patexp_used[qq], [1/3, 2/3])
    
    # Inferior tertil
    if sum(patexp_used[qq] < iq[0]) < n_iq:
        n_add = n_iq - sum(patexp_used[qq] < iq[0])
        selected_indices = patexp_used[qq] < iq[0]
        selected_indices[patexp_used[patexp_used[qq] == iq[0]].sample(n=n_add, random_state=42).index] = True
    elif sum(patexp_used[qq] < iq[0]) > n_iq:
        n_sub = sum(patexp_used[qq] < iq[0]) - n_iq
        selected_indices = patexp_used[qq] < iq[0]
        selected_indices[patexp_used[patexp_used[qq] == patexp_used[patexp_used[qq] < iq[0]][qq].max()].sample(n=n_sub, random_state=42).index] = False
    else:
        selected_indices = patexp_used[qq] < iq[0]
    patexp_used.loc[selected_indices, 'IQ'] = -1
    patexp_used.loc[selected_indices, 'IQ2'] = 0
    
    # Superior tertil
    if sum(patexp_used[qq] > iq[1]) < n_iq:
        n_add = n_iq - sum(patexp_used[qq] > iq[1])
        selected_indices = patexp_used[qq] > iq[1]
        selected_indices[patexp_used[patexp_used[qq] == iq[1]].sample(n=n_add, random_state=42).index] = True
    elif sum(patexp_used[qq] > iq[1]) > n_iq:
        n_sub = sum(patexp_used[qq] > iq[1]) - n_iq
        selected_indices = patexp_used[qq] > iq[1]
        selected_indices[patexp_used[patexp_used[qq] == patexp_used[patexp_used[qq] > iq[1]][qq].min()].sample(n=n_sub, random_state=42).index] = False
    else:
        selected_indices = patexp_used[qq] > iq[1]
    patexp_used.loc[selected_indices, 'IQ'] = 1
    patexp_used.loc[selected_indices, 'IQ2'] = 1
    
    palette = ["#2B6CB0", "#CFCFCF", "#E76F51"]
    # g=sns.displot(patexp_used, x=qq, hue='IQ', palette=palette, stat='density', alpha=0.5)
    # sns.kdeplot(data=patexp_used, x=qq, color='black', linewidth=1.8)
    # g._legend.set_title('Tertiles')
    # g._legend.get_title().set_fontsize(18)
    # new_labels = ['Low', 'Mid', 'High']
    # for t, l in zip(g._legend.texts, new_labels):
    #     t.set_text(l)
    #     t.set_fontsize(16)
    # plt.xlabel(var_corr_name[n] + ' value', fontsize=18)
    # plt.ylabel('Density', fontsize=18)
    # plt.title(var_corr_name[n] + ' distribution', fontsize=20)
    # plt.yticks(fontsize=17)
    # plt.xticks(fontsize=17)
    # plt.show()
    
    patexp_used = patexp_used.drop(patexp_used[patexp_used['IQ'] == 0].index)
    
    patexp_used['IQ_label'] = patexp_used['IQ'].map({-1: 'Low tertile', 1: 'High tertile'}) # 0: 'Mid tertile',
    
    # summary = patexp_used.groupby('IQ_label')[qq].agg(['mean', 'std', 'count'])
    # summary['sem'] = summary['std'] / np.sqrt(summary['count'])  # error estàndard de la mitjana
    # summary = summary.reindex(['Low tertile', 'High tertile'])
    
    # plt.figure(figsize=(5,4))
    # plt.bar(summary.index, summary['mean'], yerr=summary['sem'], color=["#2B6CB0", "#E76F51"],
    #     capsize=8, edgecolor='black', alpha=0.8)
    # plt.ylabel(f'Mean {var_corr_name[n]}', fontsize=18)
    # plt.xlabel('Group', fontsize=18)
    # plt.title(f'{var_corr_name[n]} by tertile group', fontsize=19)
    # plt.xticks(fontsize=17)
    # plt.yticks(fontsize=17)
    # plt.tight_layout()
    # plt.show()
    
    for pe in patexp_used.columns[:13]:
        summary = patexp_used.groupby('IQ_label')[pe].agg(['mean', 'std', 'count'])
        summary['sem'] = summary['std'] / np.sqrt(summary['count'])  # error estàndard de la mitjana
        summary = summary.reindex(['Low tertile', 'High tertile'])
        
        stat, p = ttest_ind(patexp_used[patexp_used['IQ_label'] == 'Low tertile'][pe].dropna(), 
                            patexp_used[patexp_used['IQ_label'] == 'High tertile'][pe].dropna(), equal_var=False)
        tval.loc[pe, qq] = stat
        pval.loc[pe, qq] = p
        
        plt.figure(figsize=(2.6,2))
        plt.bar(summary.index, summary['mean'], yerr=summary['sem'], color=["#2B6CB0", "#E76F51"],
            capsize=8, edgecolor='black', alpha=0.8)
        x1, x2 = 0, 1
        y = (summary['mean'].max() + summary['sem'].max())* 1.03
        h = y * 0.1  # altura de la línea
        plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c='k')
        if p <= 0.001: text = "***"
        elif p <= 0.01: text = "**"
        elif p <= 0.05: text = "*"
        elif p <= 0.1: text = "p=" + str(round(p, 2))
        else: text = "ns"
        plt.text((x1 + x2) * 0.5, (y + h)* 1.05, text, ha='center', fontsize=11)
        plt.ylim(top = (y + h)*1.25)
        plt.ylabel(f'Mean {pe}', fontsize=13)
        # plt.xlabel('Group', fontsize=13)
        # plt.title(f'{var_corr_name[n]} low-high tertiles', fontsize=14)
        plt.xticks([0, 1], ["Low\ntertile", "High\ntertile"], fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        # plt.savefig(join(savedir, 'pat_exp_distributions_final', var_corr_name[n] + '_' + pe + '.png'))
        plt.show()
    
    print('IQ = -1: ' + str(sum(patexp_used.IQ == -1)) + '; IQ = 1: ' + str(sum(patexp_used.IQ == 1)) + 
          '; IQ2 = 0: ' + str(sum(patexp_used.IQ2 == 0)) + '; IQ2 = 1: ' + str(sum(patexp_used.IQ2 == 1)))
    # print('IQ = -1: ' + str(sum(patexp_used.IQ == -1)) + '; IQ = 1: ' + str(sum(patexp_used.IQ == 1)) + '; IQ = 0: ' + str(sum(patexp_used.IQ == 0)))
    
    # colors = {0: 'blue', 1: 'green'}
    # markers = {1: 'o', -1: 'x'}  # 'o' per IQ=1, 'x' per IQ=-1

    # plt.figure(figsize=(8, 5))
    # for sex in patexp_used['Sex'].unique():
    #     for iq in patexp_used['IQ'].unique():
    #         subset = patexp_used[(patexp_used['Sex'] == sex) & (patexp_used['IQ'] == iq)]
    #         plt.scatter(
    #             subset['Age'], 
    #             subset[qq], 
    #             c=colors[sex], 
    #             marker=markers[iq], 
    #             label=f"{sex}, IQ={iq}", 
    #             alpha=0.7
    #         )
    #         # Afegim detalls al gràfic
    #         plt.xlabel('Age')
    #         plt.ylabel(qq)
    #         plt.title('Scatter plot: ' + qq + ' vs Age by Sex')
    #         plt.legend()
    #         plt.tight_layout()
    # plt.show()
    
    # patexp_used.to_excel(join(savedir, qq + '_patexp_3T.xlsx'))

tval = tval.astype(float)
pval = pval.astype(float)
tval.to_excel(join(savedir, 'TTEST_TVALUES.xlsx'))
pval.to_excel(join(savedir, 'TTEST_PVALUES.xlsx'))

#%%######################################### SCR ############################################

pca = pd.read_excel(join(savedir, 'PATTERN_EXPRESSION', 'pc1_all_data.xlsx'), index_col=0)
q =['without_EMA']
qq = 'without_EMA'

for q, e in zip(var_corr, exc_idx):    
    for qq in q:
        
        scr_used = scr_used_1.merge(var[['Age','Sex'] + q], left_index=True, right_index=True)
        scr_used = scr_used_1.merge(var[['Age','Sex']], left_index=True, right_index=True).merge(pca[q], left_index=True, right_index=True)
        scr_used = scr_used.dropna()
        # scr_used.to_excel(join(savedir, e + '_SCR.xlsx'))
        
        scr_used['IQ'] = np.zeros(scr_used.shape[0])
        scr_used['IQ2'] = np.zeros(scr_used.shape[0])
        n_iq = round(scr_used.shape[0]/3)
        iq = np.quantile(scr_used[qq], [1/3, 2/3])
        
        # Inferior tertil
        if sum(scr_used[qq] < iq[0]) < n_iq:
            n_add = n_iq - sum(scr_used[qq] < iq[0])
            selected_indices = scr_used[qq] < iq[0]
            selected_indices[scr_used[scr_used[qq] == iq[0]].sample(n=n_add, random_state=42).index] = True
        elif sum(scr_used[qq] < iq[0]) > n_iq:
            n_sub = sum(scr_used[qq] < iq[0]) - n_iq
            selected_indices = scr_used[qq] < iq[0]
            selected_indices[scr_used[scr_used[qq] == scr_used[scr_used[qq] < iq[0]][qq].max()].sample(n=n_sub, random_state=42).index] = False
        else:
            selected_indices = scr_used[qq] < iq[0]
        scr_used.loc[selected_indices, 'IQ'] = -1
        scr_used.loc[selected_indices, 'IQ2'] = 0
        
        # Superior tertil
        if sum(scr_used[qq] > iq[1]) < n_iq:
            n_add = n_iq - sum(scr_used[qq] > iq[1])
            selected_indices = scr_used[qq] > iq[1]
            selected_indices[scr_used[scr_used[qq] == iq[1]].sample(n=n_add, random_state=42).index] = True
        elif sum(scr_used[qq] > iq[1]) > n_iq:
            n_sub = sum(scr_used[qq] > iq[1]) - n_iq
            selected_indices = scr_used[qq] > iq[1]
            selected_indices[scr_used[scr_used[qq] == scr_used[scr_used[qq] > iq[1]][qq].min()].sample(n=n_sub, random_state=42).index] = False
        else:
            selected_indices = scr_used[qq] > iq[1]
        scr_used.loc[selected_indices, 'IQ'] = 1
        scr_used.loc[selected_indices, 'IQ2'] = 1
        
        scr_used = scr_used.drop(scr_used[scr_used['IQ'] == 0].index)
        
        print('IQ = -1: ' + str(sum(scr_used.IQ == -1)) + '; IQ = 1: ' + str(sum(scr_used.IQ == 1)) + 
              '; IQ2 = 0: ' + str(sum(scr_used.IQ2 == 0)) + '; IQ2 = 1: ' + str(sum(scr_used.IQ2 == 1)))

        
        colors = {0: 'blue', 1: 'green'}
        markers = {1: 'o', -1: 'x'}  # 'o' per IQ=1, 'x' per IQ=-1

        plt.figure(figsize=(8, 5))
        for sex in scr_used['Sex'].unique():
            for iq in scr_used['IQ'].unique():
                subset = scr_used[(scr_used['Sex'] == sex) & (scr_used['IQ'] == iq)]
                plt.scatter(
                    subset['Age'], 
                    subset[qq], 
                    c=colors[sex], 
                    marker=markers[iq], 
                    label=f"{sex}, IQ={iq}", 
                    alpha=0.7
                )
                # Afegim detalls al gràfic
                plt.xlabel('Age')
                plt.ylabel(qq)
                plt.title('Scatter plot: ' + qq + ' vs Age by Sex')
                plt.legend()
                plt.tight_layout()
        plt.show()
        
        scr_used.to_excel(join(savedir, qq + '_SCR.xlsx'))
        
#%% LONGITUDINAL

var_base = [['DASS_S_A', 'DASS_A_A', 'DASS_D_A'], ['SCSR_P_A'], ['STAI_T_A'], ['EMA_2weeks_first']]

var_corr = [['DASS_S_B', 'DASS_A_B', 'DASS_D_B'], ['SCSR_P_B'], ['STAI_T_B'], ['EMA_2weeks_last']]
exc_idx = ['DASS', 'SCSRP', 'STAI', 'EMA']

for q, b, e in zip(var_corr, var_base, exc_idx):    
    for qq in q:
        atexp_used = patexp_used_1.merge(var[['Age','Sex'] + q], left_index=True, right_index=True)
        patexp_used = patexp_used.dropna()
        patexp_used.to_excel(join(savedir, e + '_patexp_base.xlsx'))
        # patexp_used = patexp_used_1.merge(var[['Age','Sex'] + q + b], left_index=True, right_index=True)
        # patexp_used = patexp_used.dropna()
        # patexp_used.to_excel(join(savedir, e + '_patexp_base_long.xlsx'))
        
        patexp_used['IQ'] = np.zeros(patexp_used.shape[0])
        patexp_used['IQ2'] = np.zeros(patexp_used.shape[0])
        n_iq = round(patexp_used.shape[0]/3)
        iq = np.quantile(patexp_used[qq], [1/3, 2/3])
        
        # Inferior tertil
        if sum(patexp_used[qq] < iq[0]) < n_iq:
            n_add = n_iq - sum(patexp_used[qq] < iq[0])
            selected_indices = patexp_used[qq] < iq[0]
            selected_indices[patexp_used[patexp_used[qq] == iq[0]].sample(n=n_add, random_state=42).index] = True
        elif sum(patexp_used[qq] < iq[0]) > n_iq:
            n_sub = sum(patexp_used[qq] < iq[0]) - n_iq
            selected_indices = patexp_used[qq] < iq[0]
            selected_indices[patexp_used[patexp_used[qq] == patexp_used[patexp_used[qq] < iq[0]][qq].max()].sample(n=n_sub, random_state=42).index] = False
        else:
            selected_indices = patexp_used[qq] < iq[0]
        patexp_used.loc[selected_indices, 'IQ'] = -1
        patexp_used.loc[selected_indices, 'IQ2'] = 0
        
        # Superior tertil
        if sum(patexp_used[qq] > iq[1]) < n_iq:
            n_add = n_iq - sum(patexp_used[qq] > iq[1])
            selected_indices = patexp_used[qq] > iq[1]
            selected_indices[patexp_used[patexp_used[qq] == iq[1]].sample(n=n_add, random_state=42).index] = True
        elif sum(patexp_used[qq] > iq[1]) > n_iq:
            n_sub = sum(patexp_used[qq] > iq[1]) - n_iq
            selected_indices = patexp_used[qq] > iq[1]
            selected_indices[patexp_used[patexp_used[qq] == patexp_used[patexp_used[qq] > iq[1]][qq].min()].sample(n=n_sub, random_state=42).index] = False
        else:
            selected_indices = patexp_used[qq] > iq[1]
        patexp_used.loc[selected_indices, 'IQ'] = 1
        patexp_used.loc[selected_indices, 'IQ2'] = 1
        
        patexp_used = patexp_used.drop(patexp_used[patexp_used['IQ'] == 0].index)
        
        print('IQ = -1: ' + str(sum(patexp_used.IQ == -1)) + '; IQ = 1: ' + str(sum(patexp_used.IQ == 1)) + 
              '; IQ2 = 0: ' + str(sum(patexp_used.IQ2 == 0)) + '; IQ2 = 1: ' + str(sum(patexp_used.IQ2 == 1)))

        
        colors = {0: 'blue', 1: 'green'}
        markers = {1: 'o', -1: 'x'}  # 'o' per IQ=1, 'x' per IQ=-1

        plt.figure(figsize=(8, 5))
        for sex in patexp_used['Sex'].unique():
            for iq in patexp_used['IQ'].unique():
                subset = patexp_used[(patexp_used['Sex'] == sex) & (patexp_used['IQ'] == iq)]
                plt.scatter(
                    subset['Age'], 
                    subset[qq], 
                    c=colors[sex], 
                    marker=markers[iq], 
                    label=f"{sex}, IQ={iq}", 
                    alpha=0.7
                )
                # Afegim detalls al gràfic
                plt.xlabel('Age')
                plt.ylabel(qq)
                plt.title('Scatter plot: ' + qq + ' vs Age by Sex')
                plt.legend()
                plt.tight_layout()
        plt.show()
        
        patexp_used.to_excel(join(savedir, qq + '_patexp.xlsx'))

#%% COMPARACIÓ BASELINE - LONGITUDINAL

var_base = ['DASS_S_A', 'DASS_A_A', 'DASS_D_A', 'STAI_T_A', 'SCSR_P_A', 'EMA_2weeks_first']
var_long = ['DASS_S_B', 'DASS_A_B', 'DASS_D_B', 'SCSR_P_B', 'STAI_T_B', 'EMA_2weeks_last']

for base, long in zip(var_base, var_long):
    if 'long' in savedir:
        save_base = savedir[:-5]
        save_long = savedir
    else:
        save_base = savedir
        save_long = savedir + '_long'
    
    exc_base = pd.read_excel(join(save_base, base + '_patexp.xlsx'), index_col=0)
    exc_long = pd.read_excel(join(save_long, long + '_patexp.xlsx'), index_col=0)
    print(base)
    print(long)

#%% PCA
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import seaborn as sns

var_used1 = ['DASS_S_A', 'DASS_A_A', 'DASS_D_A', 'STAI_T_A', 'SCSR_P_A', 'EMA_2weeks_first']
var_used2 = ['DASS_S_A', 'DASS_A_A', 'DASS_D_A', 'STAI_T_A', 'SCSR_P_A']
var_used3 = ['STAI_T_A', 'SCSR_P_A']

res_pca = pd.DataFrame(index=patexp_used_1.index)

for var_used, col_name in zip([var_used1, var_used2, var_used3], ['all', 'without_EMA', 'only_DASSA_STAI_SCSRP']):
    
    var_used = var_used3
    col_name = 'anxiety_risk'
    
    data_used = var.loc[:, var_used]
    data_used = data_used.dropna()
    data_used = data_used.loc[patexp_used_1.index,:]
    
    # Data normalization
    scaler = StandardScaler()
    data_scaled = pd.DataFrame(data=scaler.fit_transform(data_used), columns=data_used.columns, index=data_used.index)
    
    pca95 = PCA(n_components=0.95)
    pca = pca95.fit_transform(data_scaled)
    df_pca = pd.DataFrame(pca[:,0], index=data_used.index, columns=[col_name])
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

##### NEW PCA -- MORE DATA
new_data = pd.read_excel('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/FIS_AX_per_Angels_27_06_25_puntuacions_totals.xlsx', 
                         index_col=0).add_prefix("sub-", axis=0)
var_used = list(new_data.columns)[3:]
var_used.remove('ASI_AxTA')
var_used.remove('PSWQ_T_A')
var_used.remove('IoUS_T_A')
new_data_used = new_data.loc[patexp.index, var_used].dropna()

# Data normalization
scaler = StandardScaler()
data_scaled = pd.DataFrame(data=scaler.fit_transform(new_data_used), columns=new_data_used.columns, index=new_data_used.index)

pca95 = PCA(n_components=0.95)
pca = pca95.fit_transform(data_scaled)
res_pca = pd.DataFrame(pca[:,0], index=new_data_used.index, columns=['PCA_F1'])

# explained_variance_ratio_ = how much variance of the total data is explained by each principal component 
plt.figure(figsize=(8, 5))
plt.bar(range(1, pca.shape[1]+1), pca95.explained_variance_ratio_, alpha=0.5, align='center', label='individual explained variance')
plt.step(range(1, pca.shape[1]+1), pca95.explained_variance_ratio_.cumsum(), where='mid', label='cumulative explained variance')
plt.axhline(y=0.95, color='r', linestyle='-')
plt.axhline(y=0.8, color='r', linestyle='-')
for i, value in enumerate(pca95.explained_variance_ratio_):
    plt.text(i + 1, value + 0.01, f"{value:.2f}", ha='center', fontsize=9)  # Ajusta el desplazamiento con `value + 0.01`
plt.ylabel('Explained variance ratio')
plt.xlabel('Principal components')
plt.title('Explained variance')
plt.legend(loc='best')
plt.show()

# Histogram (contribution of each original variable to PC1)
plt.figure(figsize=(10, 5))
plt.bar(list(new_data_used.columns), pca95.components_[0])
plt.xlabel('Original features')
plt.ylabel('Contribution')
plt.title('Contribution of original features to PC1')
plt.show()

sns.distplot(pca[:,0])
plt.xlabel('PC1 value')
plt.ylabel('Number of Cases')
plt.title('Distribution of FC1 N = ' + str(data_scaled.shape[0]))
plt.show()
#####

res_pca = pd.read_excel(join(basedir,'Mult_log_regression', 'PATTERN_EXPRESSION', 'pc1_all_data.xlsx'), index_col=0)
res_pca = pd.read_excel(join(basedir,'Mult_log_regression', 'PATTERN_EXPRESSION_xval', 'pc1_anxiety_risk.xlsx'), index_col=0)

for qq in res_pca.columns:
    # qq = res_pca.columns[0]
    patexp_used = patexp_used_1.merge(var[['Age_A','Sex']], left_index=True, right_index=True).merge(res_pca[qq], left_index=True, right_index=True)
    patexp_used = patexp_used.dropna()
    # patexp_used.to_excel(join(savedir, qq + '_all_patexp.xlsx'))
    
    # Check continuos correlation (pearson correlation)
    pearsonr(patexp_used[qq], patexp_used['reddan_CS+'])
    pearsonr(patexp_used[qq], patexp_used['reddan_CS-'])
    pearsonr(patexp_used[qq], patexp_used['reddan_CS+'] - patexp_used['reddan_CS-'])
    
    sns.regplot(x=patexp_used[qq], y=patexp_used['CS+'] - patexp_used['CS-'])
    plt.xlabel('CS+ - CS-')
    plt.ylabel('Anxiety index')
    
    patexp_used['IQ'] = np.zeros(patexp_used.shape[0])
    # patexp_used['IQ2'] = np.zeros(patexp_used.shape[0])
    n_iq = round(patexp_used.shape[0]/3)
    iq = np.quantile(patexp_used[qq], [1/3, 2/3])
    
    # Inferior tertil
    if sum(patexp_used[qq] < iq[0]) < n_iq:
        n_add = n_iq - sum(patexp_used[qq] < iq[0])
        selected_indices = patexp_used[qq] < iq[0]
        selected_indices[patexp_used[patexp_used[qq] == iq[0]].sample(n=n_add, random_state=42).index] = True
    elif sum(patexp_used[qq] < iq[0]) > n_iq:
        n_sub = sum(patexp_used[qq] < iq[0]) - n_iq
        selected_indices = patexp_used[qq] < iq[0]
        selected_indices[patexp_used[patexp_used[qq] == patexp_used[patexp_used[qq] < iq[0]][qq].max()].sample(n=n_sub, random_state=42).index] = False
    else:
        selected_indices = patexp_used[qq] < iq[0]
    patexp_used.loc[selected_indices, 'IQ'] = -1
    patexp_used.loc[selected_indices, 'IQ2'] = 0
    
    # Superior tertil
    if sum(patexp_used[qq] > iq[1]) < n_iq:
        n_add = n_iq - sum(patexp_used[qq] > iq[1])
        selected_indices = patexp_used[qq] > iq[1]
        selected_indices[patexp_used[patexp_used[qq] == iq[1]].sample(n=n_add, random_state=42).index] = True
    elif sum(patexp_used[qq] > iq[1]) > n_iq:
        n_sub = sum(patexp_used[qq] > iq[1]) - n_iq
        selected_indices = patexp_used[qq] > iq[1]
        selected_indices[patexp_used[patexp_used[qq] == patexp_used[patexp_used[qq] > iq[1]][qq].min()].sample(n=n_sub, random_state=42).index] = False
    else:
        selected_indices = patexp_used[qq] > iq[1]
    patexp_used.loc[selected_indices, 'IQ'] = 1
    patexp_used.loc[selected_indices, 'IQ2'] = 1
    
    g=sns.displot(patexp_used, x=qq, hue='IQ', palette=palette, stat='density', alpha=0.5)
    sns.kdeplot(data=patexp_used, x=qq, color='black', linewidth=1.8)
    g._legend.set_title('Tertiles')
    g._legend.get_title().set_fontsize(18)
    new_labels = ['Low', 'Mid', 'High']
    for t, l in zip(g._legend.texts, new_labels):
        t.set_text(l)
        t.set_fontsize(16)
    plt.xlabel('PC1 value', fontsize=18)
    plt.ylabel('Density', fontsize=18)
    plt.title('PC1 distribution', fontsize=20)
    plt.yticks(fontsize=17)
    plt.xticks(fontsize=17)
    plt.show()
    
    patexp_used = patexp_used.drop(patexp_used[patexp_used['IQ'] == 0].index)
    
    patexp_used['IQ_label'] = patexp_used['IQ'].map({-1: 'Low tertile', 1: 'High tertile'})
    
    summary = patexp_used.groupby('IQ_label')[qq].agg(['mean', 'std', 'count'])
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
        
    print('IQ = -1: ' + str(sum(patexp_used.IQ == -1)) + '; IQ = 1: ' + str(sum(patexp_used.IQ == 1)) + 
          '; IQ2 = 0: ' + str(sum(patexp_used.IQ2 == 0)) + '; IQ2 = 1: ' + str(sum(patexp_used.IQ2 == 1)))
    
    # colors = {0: 'blue', 1: 'green'}
    # markers = {1: 'o', -1: 'x'}  # 'o' per IQ=1, 'x' per IQ=-1

    # plt.figure(figsize=(8, 5))
    # for sex in patexp_used['Sex'].unique():
    #     for iq in patexp_used['IQ'].unique():
    #         subset = patexp_used[(patexp_used['Sex'] == sex) & (patexp_used['IQ'] == iq)]
    #         plt.scatter(
    #             subset['Age'], 
    #             subset[qq], 
    #             c=colors[sex], 
    #             marker=markers[iq], 
    #             label=f"{sex}, IQ={iq}", 
    #             alpha=0.7
    #         )
    #         # Afegim detalls al gràfic
    #         plt.xlabel('Age')
    #         plt.ylabel(qq)
    #         plt.title('Scatter plot: ' + qq + ' vs Age by Sex')
    #         plt.legend()
    #         plt.tight_layout()
    # plt.show()
    
    patexp_used.to_excel(join(savedir, qq + '_patexp_3T.xlsx'))


## Relation subjective responses with questionnaires
subj_rat_used = subj_rat.loc[patexp_used_1.index,:]

subj_resp_vars = ['COND_CSplus_ARO', 'COND_Csminus_ARO', 'COND_CSplus_VAL', 'COND_CSminus_VAL',
                  'REV_New_CSplus_ARO', 'REV_New_CSminus_ARO', 'REV_New_Csplus_VAL', 'REV_New_CSminus_VAL']

anxiety_vars = {'SCSR_P_A': var.loc[subj_rat_used.index, 'SCSR_P_A'], 'STAI_T_A': var.loc[subj_rat_used.index, 'STAI_T_A'], 'PCA': res_pca}


r_results = pd.DataFrame(columns=['SCSR_P_A', 'STAI_T_A', 'PCA'], index=subj_resp_vars)
p_results = pd.DataFrame(columns=['SCSR_P_A', 'STAI_T_A', 'PCA'], index=subj_resp_vars)
for anx_name, anxiety_var in anxiety_vars.items():
    for subj_resp in subj_resp_vars:
        
        if 'VAL' in subj_resp:
            data = (pd.concat([(subj_rat_used[subj_resp] - 6) * -1, anxiety_var], axis=1).dropna())
        else:
            data = (pd.concat([subj_rat_used[subj_resp], anxiety_var], axis=1).dropna())

        x = data.iloc[:, 0]
        y = data.iloc[:, 1]

        r, p = pearsonr(x, y)
        r_results.loc[subj_resp, anx_name] = r
        p_results.loc[subj_resp, anx_name] = p
        
        plt.figure(figsize=(6, 4))
        sns.regplot(x=x, y=y)
        plt.title(f'{subj_resp} vs {anx_name}\n' f'r = {r:.3f}, p = {p:.3g}')
        plt.xlabel(subj_resp)
        plt.ylabel(anx_name)
        plt.tight_layout()
        plt.show()

r_results = r_results.astype(float)
sns.heatmap(r_results, annot=True, fmt=".2f", cmap="coolwarm", square=True)

mask = p_results > 0.05
p_results = p_results.astype(float)
sns.heatmap(p_results, mask=mask, annot=False, fmt=".2f", cmap="autumn_r", vmax=0.05, square=True)






















