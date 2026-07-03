#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 15:56:41 2024

@author: acalvet

Check data
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tools.tools import add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor
from collections import Counter
from os.path import join
from sklearn.linear_model import LassoCV, RidgeCV, ElasticNetCV, LogisticRegression, LinearRegression, LogisticRegressionCV
from sklearn.model_selection import KFold, StratifiedKFold, permutation_test_score, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, recall_score, make_scorer

    
subbase = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git'
basedir = join(subbase, 'results', 'final_brainmask')
savedir = join(basedir, 'Mult_log_regression', 'PATTERN_EXPRESSION_xval', 'feature_selection_method')

patexp = pd.read_excel(join(basedir, '2_SVM_results_stai', 'pat_exp_all_data_xval.xlsx'), index_col=0)
df_var = pd.read_excel(join(subbase, 'FIS_AX_per_Angels_27_06_25_puntuacions_totals.xlsx'), index_col=0).add_prefix("sub-", axis=0)
pca_f1 = pd.read_excel(join(basedir, 'Mult_log_regression', 'PATTERN_EXPRESSION', 'pc1_all_data.xlsx'), index_col=0)['without_EMA']
df_var['PCA1_F1'] = pca_f1
    
# var = ['ASI_AxTA', 'DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'IoUS_T_A', 'LSAS_T_A', 'PSWQ_T_A', 'SCSR_P_A', 'STAI_T_A', 'TAG_T_A', 'PCA1_F1']
var = ['DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'SCSR_P_A', 'STAI_T_A', 'PCA1_F1']
var = ['SCSR_P_A', 'STAI_T_A']

n_permut=5000
cv_metrics = []

# Example:
# df = pd.read_csv("behavior.csv", index_col="SubjID")
# df_cytof_filtered = pd.read_csv("cytof_data.csv", index_col="SubjID")

for v in var:
    print('##################################### ' + v + ' #####################################')
    # Drop unwanted columns
    df_filtered = patexp.drop(columns=['CS+', 'CS-', 'CS+rev', 'CS-rev'], errors='ignore')
    df_filtered[v] = df_var[v]
    df_filtered = df_filtered.loc[:, ['CS+early', 'CS+late', 'CS-early', 'CS-late', v]]
    
    df_filtered["group"] = df_filtered.index.to_series().str.contains("P").astype(int)
    
    
    # Logistic Regression Model WITHOUT FEATURE SELECTION
    print('Logistic Regression Model with permutation')
    X_final = df_filtered.iloc[:,:-2]
    y_final_log = df_filtered.group
    
    # Sensitivity = recall de la clase 1 (ansiedad alta)
    sensitivity = make_scorer(recall_score, pos_label=1)
    
    # Specificity = recall de la clase 0 (ansiedad baja)
    specificity = make_scorer(recall_score, pos_label=0)
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    logmodel_noreg = make_pipeline(StandardScaler(), LogisticRegressionCV())
    cv_results_log, perm_scores, pval_log = permutation_test_score(logmodel_noreg, X_final, y_final_log, cv=cv, scoring="accuracy", 
                                                                   n_permutations=n_permut, random_state=42, n_jobs=1)
    
    scores_log_noreg = cross_val_score(logmodel_noreg, X_final, y_final_log, cv=cv, scoring='accuracy')
    scores_log_noreg_sens = cross_val_score(logmodel_noreg, X_final, y_final_log, cv=cv, scoring=sensitivity)
    scores_log_noreg_spec = cross_val_score(logmodel_noreg, X_final, y_final_log, cv=cv, scoring=specificity)
    
    plt.plot(scores_log_noreg, marker='o')
    plt.axhline(0.5, linestyle='--', color='red')
    plt.axhline(scores_log_noreg.mean(), color='yellow')
    plt.axhline(perm_scores1.mean(), color='orange')
    plt.ylabel('Fold acc')
    plt.xlabel('Fold')
    plt.legend(['CV acc', 'chance', 'mean CV acc', 'mean permutation acc'])
    plt.show()
    
    plt.plot(perm_scores1, marker='.')
    plt.axhline(0.5, linestyle='--', color='red')
    plt.ylabel('Permutation acc')
    plt.xlabel('Permutation')
    plt.show()
    
    betas = []
    for train_idx, test_idx in cv.split(X_final, y_final_log):
        X_train = X_final.iloc[train_idx]
        y_train = y_final_log.iloc[train_idx]
        logmodel_noreg = make_pipeline(StandardScaler(), LogisticRegressionCV())
        logmodel_noreg.fit(X_train, y_train)
        betas.append(logmodel_noreg.named_steps['logisticregressioncv'].coef_)
    
    cv_metrics_log.append({"Variable": v, "Accuracy": cv_results_log1, "Sens": scores_log_noreg_sens.mean(), "Spec": scores_log_noreg_spec.mean(), 
                           "pval": pval_log1, "acc_CV": scores_log_noreg, "Betas": list(X_final.columns),
                           "Betas_mean": np.mean(betas, axis=0), "Betas_std": np.std(betas, axis=0)})






    # Linear Regression Model
    print('Linear Regression Model with permutation')
    df_filtered = df_filtered.dropna()
    X_final = add_constant(df_filtered.iloc[:,:-1])
    y_final = df_filtered.loc[:,v]
    
    cv = KFold(n_splits=10, shuffle=True, random_state=42)
    
    # grid de alphas (equivalente a C)
    alphas = np.logspace(-3, 1, 10)
    l1_ratios = [0.1, 0.5, 0.7, 0.9, 1]
    
    
    linear = make_pipeline(StandardScaler(), LinearRegression())
    cv_r2_linear, perm_linear, pval_linear = permutation_test_score(linear, X_final, y_final, cv=cv, scoring="r2",
                                                                    n_permutations=n_permut, random_state=42, n_jobs=1)
    scores_linear = cross_val_score(linear, X_final, y_final, cv=cv, scoring='r2')
    
    plt.plot(scores_linear, marker='o')
    plt.axhline(0, linestyle='--', color='red')
    plt.axhline(scores_linear.mean(), color='yellow')
    plt.axhline(perm_linear.mean(), color='orange')
    plt.ylabel('Fold R²')
    plt.xlabel('Fold')
    plt.legend(['CV R²', 'chance', 'mean CV R²', 'mean permutation R²'])
    plt.show()
    
    plt.plot(perm_linear, marker='.')
    plt.axhline(0, linestyle='--', color='red')
    plt.ylabel('Permutation R²')
    plt.xlabel('Permutation')
    plt.show()
    
    betas_linear = []
    for train_idx, test_idx in cv.split(X_final):
        X_train = X_final.iloc[train_idx]
        y_train = y_final.iloc[train_idx]
        linear = make_pipeline(StandardScaler(), LinearRegression())
        linear.fit(X_train, y_train)
        betas_linear.append(linear.named_steps['linearregression'].coef_)
    
    cv_metrics.append({"Variable": v, "R2_linear": cv_r2_linear, "pval_linear": pval_linear,
                       "R2_folds": scores_linear, "betas_linear_mean": np.mean(betas_linear, axis=0), 
                       "betas_linear_std": np.std(betas_linear, axis=0), "betas_linear": betas_linear})


    
cv_metrics_df = pd.DataFrame(cv_metrics).set_index("Variable")
cv_metrics_df.to_excel(join(savedir, "linear_model_summary_10f_" + str(n_permut) + "_all_DATA_elastic_ALL.xlsx"))

cv_metrics_df = pd.DataFrame(cv_metrics).set_index("Variable")
cv_metrics_df.to_excel(join(savedir, "linear_model_summary_10f_" + str(n_permut) + "_" + v + ".xlsx"))

