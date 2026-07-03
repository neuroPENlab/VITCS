#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Fri Oct 11 15:56:41 2024

@author: acalvet

Check data
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tools.tools import add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor
from collections import Counter
from os.path import join
from sklearn.linear_model import LogisticRegression, LinearRegression, LogisticRegressionCV
from sklearn.model_selection import KFold, StratifiedKFold, permutation_test_score, cross_val_predict, cross_val_score
from sklearn.metrics import accuracy_score, recall_score, make_scorer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

    
subbase = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git'
basedir = join(subbase, 'results', 'final_brainmask', 'Mult_log_regression', 'PATTERN_EXPRESSION_xval')
# basedir = join(subbase, 'results', 'final_brainmask', 'Mult_log_regression', 'PATTERN_EXPRESSION_suitas')
savedir = join(basedir, 'feature_selection_method')

var = ['DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'PCA1_F1'] #, 'SCSR_P_A', 'STAI_T_A'
# var = ['SCSR_P_A', 'STAI_T_A']
n_permut = 5000
cv_metrics_log = []

for v in var:
    print('##################################### ' + v + ' #####################################')
    # Drop unwanted columns
    
    df_original = pd.read_excel(join(basedir, v + '_patexp.xlsx'), index_col=0)
    # df_original.columns = df_original.columns.str.replace('suitas_', '')
    
    # df_filtered = df_original.loc[:, ['CS+early', 'CS+late', 'CS-early', 'CS-late', 
    #                                   'CS+revearly','CS+revlate', 'CS-revearly', 'CS-revlate', v]]
    df_filtered = df_original.loc[:, ['CS+early', 'CS+late', 'CS-early', 'CS-late', v]]
    # df_filtered = df_original.loc[:, ['CS+revearly','CS+revlate', 'CS-revearly', 'CS-revlate', v]]

    print('Logistic Regression Model with permutation')
    X_final = df_filtered.iloc[:,:-1]
    y_final_log = df_original.IQ2
    
    # Sensitivity = recall de la clase 1 (ansiedad alta)
    sensitivity = make_scorer(recall_score, pos_label=1)
    
    # Specificity = recall de la clase 0 (ansiedad baja)
    specificity = make_scorer(recall_score, pos_label=0)
    
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    logmodel_noreg = make_pipeline(StandardScaler(), LogisticRegressionCV())
    cv_results_log1, perm_scores1, pval_log1 = permutation_test_score(logmodel_noreg, X_final, y_final_log, cv=cv, scoring="accuracy", 
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

    
    # Cs = [0.001, 0.01, 0.1, 1, 10]
    # l1_ratios = [0.1, 0.5, 0.9]
    # logmodel = make_pipeline(StandardScaler(), LogisticRegressionCV(Cs=Cs, penalty='elasticnet', solver='saga',
    #                                                                 l1_ratios=l1_ratios, cv=5, max_iter=1000, n_jobs=1))
    # #logmodel = LogisticRegressionCV(Cs=Cs, penalty='l1', solver='liblinear', cv=5, max_iter=1000, n_jobs=1)
    
    # cv_results_log, perm_scores, pval_log = permutation_test_score(logmodel, X_final, y_final_log, cv=cv, scoring="accuracy", 
    #                                                                n_permutations=n_permut, random_state=42, n_jobs=1)
    # scores_log = cross_val_score(logmodel, X_final, y_final_log, cv=cv, scoring='accuracy')
    # plt.plot(scores_log, marker='o')
    # plt.axhline(0.5, linestyle='--', color='red')
    # plt.axhline(scores_log.mean(), color='yellow')
    # plt.axhline(perm_scores.mean(), color='orange')
    # plt.ylabel('Fold acc')
    # plt.xlabel('Fold')
    # plt.legend(['CV acc', 'chance', 'mean CV acc', 'mean permutation acc'])
    # plt.show()
    
    # plt.plot(perm_scores1, marker='.')
    # plt.axhline(0.5, linestyle='--', color='red')
    # plt.ylabel('Permutation acc')
    # plt.xlabel('Permutation')
    # plt.show()
        
    # y_prob = cross_val_predict(logmodel, X_final, y_final_log, cv=cv, method="predict_proba")[:,1] # high tertil probability
    # y_pred = (y_prob > 0.5).astype(int)
    # acc_cv = accuracy_score(y_final_log, y_pred)
    # sens_cv = recall_score(y_final_log, y_pred, pos_label=1)
    # spec_cv = recall_score(y_final_log, y_pred, pos_label=0)
    
    # betas = []
    # betasperc = []
    # acc = []
    # Cbest = []
    # l1best = []
    # for train_idx, test_idx in cv.split(X_final, y_final_log):
    #     model_log = logmodel.fit(X_final.iloc[train_idx], y_final_log.iloc[train_idx])
    #     acc.append(model_log.score(X_final.iloc[test_idx], y_final_log.iloc[test_idx]))
    #     clf = model_log.named_steps['logisticregressioncv']
    #     betas.append(clf.coef_.ravel()) #.ravel()
    #     betasperc.append((clf.coef_.ravel() != 0).astype(int)) # .ravel()
    #     Cbest.append(clf.C_)
    #     l1best.append(clf.l1_ratio_)
    # betas = np.array(betas)

    # logmodel.fit(X_final, y_final_log)
    # clf_final = logmodel.named_steps['logisticregressioncv']
    # cv_metrics_log.append({"Variable": v, "Accuracy": acc_cv, "Acc_perm": cv_results_log, "Sens": sens_cv, "Spec": spec_cv, 
    #                        "pval": pval_log, "acc_CV": acc, "Betas": list(X_final.columns), "Betas%": sum(betasperc)*10,
    #                        "Betas_mean": np.nanmean(np.where(betas == 0, np.nan, betas), axis=0), "Betas_std": np.nanstd(np.where(betas == 0, np.nan, betas), axis=0), 
    #                        'Betas_final': clf_final.coef_, 'C_best': Cbest, 'C_best_final': clf_final.C_, 'L1_best': l1best, "l1_ratio_final": clf_final.l1_ratio_})   
    
    
    # df_plot = pd.DataFrame({"Prob_high": y_prob, "Group": y_final_log})
    
    # palette = {"0": "#2B6CB0", "1": "#E76F51"}
    
    # plt.figure(figsize=(6,5.5))
    # ax = sns.boxplot(data=df_plot, x="Group", y="Prob_high", palette=palette, width=0.5, showfliers=False, 
    #                  boxprops=dict(linewidth=2), whiskerprops=dict(linewidth=2), capprops=dict(linewidth=2), medianprops=dict(linewidth=2.5))
    # sns.stripplot(data=df_plot, x="Group", y="Prob_high", color="black", alpha=0.35, jitter=0.15, size=4)
    # plt.axhline(0.5, linestyle="--", color="red", linewidth=2)
    # plt.ylabel("Predicted probability\nLOW <-----------------> HIGH\nTERTIL                      TERTIL", fontsize=25)
    # plt.xlabel("")
    # plt.ylim([0, 1])
    # plt.xticks([0, 1], ["True low\ntertil", "True high\ntertil"], fontsize=25)
    # # plt.title(v + " model decision", fontsize=20)
    # plt.yticks(fontsize=23)
    # sns.despine()
    # plt.tight_layout()
    # plt.savefig(join(savedir, v +"_model_decision_COND_2.png"))
        
cv_metrics_log_df = pd.DataFrame(cv_metrics_log).set_index("Variable")
cv_metrics_log_df.to_excel(join(savedir, "logistic_model_summary_10f_" + str(n_permut) + "_DASS.xlsx"))
