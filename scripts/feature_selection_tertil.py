#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Saül Pascual-Diaz"
__institution__ = "University of Barcelona"
__date__ = "2025/06/08"
__version__ = "1"
__status__ = "Stable"

"""
Modified by Àngels Calvet

Feature selection and linear modeling pipeline for predicting PedsQL Physical scores
from CyTOF-derived immature neutrophil signaling markers in adolescents.

Steps:
1. Variance Inflation Factor (VIF) filtering to control collinearity
2. Bootstrapped stepwise selection (OLS, based on p-values)
3. Stable feature detection (selected in >50% of bootstraps)
4. Final OLS model fit with selected predictors
5. Optional: summary plot and CSV exports
"""

# Imports
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

# VIF
def filter_by_vif(X, threshold=10.0):
    """
    Iteratively removes variables with VIF above threshold.
    """
    variables = X.columns.tolist()
    while True:
        dropped = False
        X_const = add_constant(X[variables])
        vif = pd.Series(
            [variance_inflation_factor(X_const.values, i) for i in range(X_const.shape[1])],
            index=['const'] + variables
        )
        max_vif = vif[1:].max()
        if max_vif > threshold:
            drop_var = vif[1:].idxmax()
            print(f"⚠️ Dropping '{drop_var}' due to high VIF: {vif[drop_var]:.2f}")
            variables.remove(drop_var)
            dropped = True
        if not dropped:
            break
    return variables

# Stepwise regression
def stepwise_selection(X, y, initial_list=None, threshold_in=0.01, threshold_out=0.05, verbose=False):
    """
    Forward-backward stepwise feature selection using OLS p-values.
    """
    if initial_list is None:
        initial_list = []
    included = list(initial_list)
    while True:
        changed = False
        # Forward step
        excluded = list(set(X.columns) - set(included))
        new_pval = pd.Series(index=excluded, dtype=float)
        for col in excluded:
            model = sm.OLS(y, add_constant(X[included + [col]])).fit()
            new_pval[col] = model.pvalues[col]
        if not new_pval.empty:
            best_p = new_pval.min()
            if best_p < threshold_in:
                best_feat = new_pval.idxmin()
                included.append(best_feat)
                changed = True
                if verbose:
                    print(f"  + Add {best_feat:30} p={best_p:.4f}")
        # Backward step
        if included:
            model = sm.OLS(y, add_constant(X[included])).fit()
            pvalues = model.pvalues.iloc[1:]  # Exclude const
            worst_p = pvalues.max()
            if worst_p > threshold_out:
                worst_feat = pvalues.idxmax()
                included.remove(worst_feat)
                changed = True
                if verbose:
                    print(f"  - Drop {worst_feat:30} p={worst_p:.4f}")
        if not changed:
            break
    return included

# Bootstrap
def bootstrap_selection_vif(df, target_col, vif_thresh=10.0, n_bootstraps=500,
                             threshold_in=0.05, threshold_out=0.1, verbose=True):
    """
    Runs VIF filtering and bootstrapped stepwise selection.
    Returns selection frequencies dictionary.
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]

    keep_vars = filter_by_vif(X, threshold=vif_thresh)
    X = X[keep_vars]
    df_filtered = pd.concat([X, y], axis=1)

    counts = Counter()
    for i in range(n_bootstraps):
        sample_idx = np.random.choice(df_filtered.index, size=len(df_filtered), replace=True)
        X_sample = df_filtered.loc[sample_idx, keep_vars]
        y_sample = df_filtered.loc[sample_idx, target_col]
        selected = stepwise_selection(X_sample, y_sample,
                                      threshold_in=threshold_in,
                                      threshold_out=threshold_out)
        counts.update(selected)
        if verbose and (i + 1) % 50 == 0:
            print(f"Bootstrap {i + 1}/{n_bootstraps}")
    freqs = {var: counts[var] / n_bootstraps for var in keep_vars}
    return freqs

# Main
if __name__ == "__main__":
    # Load or prepare data manually in the notebook context
    
    subbase = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git'
    basedir = join(subbase, 'results', 'final_brainmask', 'Mult_log_regression', 'PATTERN_EXPRESSION_xval')
    savedir = join(basedir, 'feature_selection_method')
    
    # var = ['ASI_AxTA', 'DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'IoUS_T_A', 'LSAS_T_A', 'PSWQ_T_A', 'SCSR_P_A', 'STAI_T_A', 'TAG_T_A', 'PCA1_F1']
    var = ['DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'SCSR_P_A', 'STAI_T_A', 'PCA1_F1']
    feat_selection = pd.read_excel(join(savedir, 'feature_selection_VITS.xlsx'), index_col=0)
    
    n_permut = 5000
    
    cv_metrics = []
    cv_metrics_log = []
    # Example:
    # df = pd.read_csv("behavior.csv", index_col="SubjID")
    # df_cytof_filtered = pd.read_csv("cytof_data.csv", index_col="SubjID")

    for v in var:
        print('##################################### ' + v + ' #####################################')
        # Drop unwanted columns
        
        df_original = pd.read_excel(join(basedir, v + '_patexp.xlsx'), index_col=0)
        # df_original.columns = df_original.columns.str.replace('reddan_', '')
        # df_filtered = df_original.loc[:, ['CS+early', 'CS+late', 'CS-early', 'CS-late', 
        #                                   'CS+revearly','CS+revlate', 'CS-revearly', 'CS-revlate', v]]
        df_filtered = df_original.loc[:, ['CS+early', 'CS+late', 'CS-early', 'CS-late', v]]
        # df_filtered = df_original.loc[:, ['CS+revearly','CS+revlate', 'CS-revearly', 'CS-revlate', v]]
    
        # # Run pipeline
        # freqs = bootstrap_selection_vif(
        #     df_filtered,
        #     target_col=v,
        #     vif_thresh=10.0,
        #     n_bootstraps=500,
        #     threshold_in=0.05,
        #     threshold_out=0.10,
        #     verbose=True
        # )
    
        # # Display selection frequencies
        # sorted_freqs = dict(sorted(freqs.items(), key=lambda x: x[1], reverse=True))
        # print("\nSelection frequencies:")
        # for var, f in sorted_freqs.items():
        #     print(f"  {var:40} {f:.2%}")
    
        # # Identify stable predictors
        # stable_vars = [var for var, freq in sorted_freqs.items() if freq > 0.5]
        # print("\nStable predictors (freq >50%):", stable_vars)
        
        # stable_vars = feat_selection.loc[v, :][feat_selection.loc[v, :] == 1].index.tolist()
        
        # Final model
        # if stable_vars:
            # X_final = add_constant(df_filtered[stable_vars])

            # # Linear Regression Model
            # y_final = df_filtered[v]
            
            # print('Linear Regression Model with permutation')
            # cv = KFold(n_splits=10, shuffle=True, random_state=42)
            # cv_results, perm_scores, pval = permutation_test_score(LinearRegression(), X_final, y_final, cv=cv,
            #                                                        scoring="r2", n_permutations=n_permut, random_state=42)
            
            # betas = []
            # r2 = []
            # for train_idx, test_idx in cv.split(X_final, y_final):
            #     model = LinearRegression().fit(X_final.iloc[train_idx], y_final.iloc[train_idx])
            #     r2.append(model.score(X_final.iloc[test_idx], y_final.iloc[test_idx]))
            #     betas.append(model.coef_)
            
            # betas = np.array(betas)
            
            # cv_metrics.append({"Variable": v, "R2": cv_results, "pval": pval, "R2_CV": r2, 
            #                    "Betas": list(X_final.columns), "Betas_mean": betas.mean(axis=0), "Betas_std": betas.std(axis=0)})
            
            
            # # Logistic Regression Model
            # print('Logistic Regression Model with permutation')
            
            # # Sensitivity = recall de la clase 1 (ansiedad alta)
            # sensitivity = make_scorer(recall_score, pos_label=1)
            
            # # Specificity = recall de la clase 0 (ansiedad baja)
            # specificity = make_scorer(recall_score, pos_label=0)
            
            # y_final_log = df_original.IQ2
            
            # cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
            
            # cv_results_log, perm_scores, pval_log = permutation_test_score(LogisticRegression(max_iter=1000), X_final, y_final_log, 
            #                                                                cv=cv, scoring="accuracy", n_permutations=n_permut, random_state=42)
            
            # cv_results_sens, perm_scores_sens, pval_sens = permutation_test_score(LogisticRegression(max_iter=1000), X_final, y_final_log,
            #                                                                       cv=cv, scoring=sensitivity, n_permutations=n_permut, random_state=42)

            # cv_results_spec, perm_scores_spec, pval_spec = permutation_test_score(LogisticRegression(max_iter=1000), X_final, y_final_log,
            #                                                                       cv=cv, scoring=specificity, n_permutations=n_permut, random_state=42)
            
            
            # from sklearn.model_selection import cross_val_predict
            # model = LogisticRegression(max_iter=1000)
            # y_prob = cross_val_predict(model, X_final, y_final_log, cv=cv, method="predict_proba")[:,1]
            
            # df_plot = pd.DataFrame({"Prob_high": y_prob, "Group": y_final_log})
            
            # palette = {"0": "#2B6CB0", "1": "#E76F51"}
            
            # plt.figure(figsize=(6,6))
            # ax = sns.boxplot(data=df_plot, x="Group", y="Prob_high", palette=palette, width=0.5, showfliers=False, 
            #                  boxprops=dict(linewidth=2), whiskerprops=dict(linewidth=2), capprops=dict(linewidth=2), medianprops=dict(linewidth=2.5))
            # sns.stripplot(data=df_plot, x="Group", y="Prob_high", color="black", alpha=0.35, jitter=0.15, size=4)
            # plt.axhline(0.5, linestyle="--", color="red", linewidth=2)
            # plt.ylabel("Predicted probability\nLOW <----------------------------------> HIGH", fontsize=20)
            # plt.xlabel("")
            # plt.ylim([0, 1])
            # plt.xticks([0, 1], ["True low tertil", "True high tertil"], fontsize=20)
            # # plt.title(v + " model decision", fontsize=20)
            # plt.yticks(fontsize=18)
            # sns.despine()
            # plt.tight_layout()
            # plt.savefig(join(savedir, v +"_model_decision.png"))
            
            # betas = []
            # acc = []
            # for train_idx, test_idx in cv.split(X_final, y_final_log):
            #     model_log = LogisticRegression(max_iter=1000).fit(X_final.iloc[train_idx], y_final_log.iloc[train_idx])
            #     acc.append(model_log.score(X_final.iloc[test_idx], y_final_log.iloc[test_idx]))
            #     betas.append(model_log.coef_)
                
            
            # betas = np.array(betas)
            
            # cv_metrics_log.append({"Variable": v, "Accuracy": cv_results_log, "Sens": cv_results_sens, "Spec": cv_results_spec, 
            #                        "pval": pval_log, "acc_CV": acc, "Betas": list(X_final.columns), "Betas_mean": betas.mean(axis=0), 
            #                        "Betas_std": betas.std(axis=0), "Accuracy2": model_log2.score(X_final, y_final_log), "Betas2": model_log2.coef_})
        
        # X_final = add_constant(df_filtered[stable_vars])

        # # Linear Regression Model
        # y_final = df_filtered[v]
        
        # print('Linear Regression Model with permutation')
        # cv = KFold(n_splits=10, shuffle=True, random_state=42)
        # cv_results, perm_scores, pval = permutation_test_score(LinearRegression(), X_final, y_final, cv=cv,
        #                                                        scoring="r2", n_permutations=n_permut, random_state=42)
        
        # betas = []
        # r2 = []
        # for train_idx, test_idx in cv.split(X_final, y_final):
        #     model = LinearRegression().fit(X_final.iloc[train_idx], y_final.iloc[train_idx])
        #     r2.append(model.score(X_final.iloc[test_idx], y_final.iloc[test_idx]))
        #     betas.append(model.coef_)
        
        # betas = np.array(betas)
        
        # cv_metrics.append({"Variable": v, "R2": cv_results, "pval": pval, "R2_CV": r2, 
        #                    "Betas": list(X_final.columns), "Betas_mean": betas.mean(axis=0), "Betas_std": betas.std(axis=0)})
        
        # else:
        #     print("No predictors passed the stability threshold.")
        
        # Logistic Regression Model WITHOUT FEATURE SELECTION
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



        
        Cs = [0.001, 0.01, 0.1, 1, 10]
        l1_ratios = [0.1, 0.5, 0.9]
        logmodel = make_pipeline(StandardScaler(), LogisticRegressionCV(Cs=Cs, penalty='elasticnet', solver='saga',
                                                                        l1_ratios=l1_ratios, cv=5, max_iter=1000, n_jobs=1))
        #logmodel = LogisticRegressionCV(Cs=Cs, penalty='l1', solver='liblinear', cv=5, max_iter=1000, n_jobs=1)
        
        cv_results_log, perm_scores, pval_log = permutation_test_score(logmodel, X_final, y_final_log, cv=cv, scoring="accuracy", 
                                                                       n_permutations=n_permut, random_state=42, n_jobs=1)
        scores_log = cross_val_score(logmodel, X_final, y_final_log, cv=cv, scoring='accuracy')
        plt.plot(scores_log, marker='o')
        plt.axhline(0.5, linestyle='--', color='red')
        plt.axhline(scores_log.mean(), color='yellow')
        plt.axhline(perm_scores.mean(), color='orange')
        plt.ylabel('Fold acc')
        plt.xlabel('Fold')
        plt.legend(['CV acc', 'chance', 'mean CV acc', 'mean permutation acc'])
        plt.show()
        
        plt.plot(perm_scores1, marker='.')
        plt.axhline(0.5, linestyle='--', color='red')
        plt.ylabel('Permutation acc')
        plt.xlabel('Permutation')
        plt.show()
        
        # cv_results_sens, perm_scores_sens, pval_sens = permutation_test_score(logmodel, X_final, y_final_log, cv=cv, scoring=sensitivity, 
        #                                                                       n_permutations=n_permut, random_state=42, n_jobs=1)

        # cv_results_spec, perm_scores_spec, pval_spec = permutation_test_score(logmodel, X_final, y_final_log, cv=cv, scoring=specificity, 
        #                                                                       n_permutations=n_permut, random_state=42, n_jobs=1)
        
        y_prob = cross_val_predict(logmodel, X_final, y_final_log, cv=cv, method="predict_proba")[:,1] # high tertil probability
        y_pred = (y_prob > 0.5).astype(int)
        acc_cv = accuracy_score(y_final_log, y_pred)
        sens_cv = recall_score(y_final_log, y_pred, pos_label=1)
        spec_cv = recall_score(y_final_log, y_pred, pos_label=0)
        
        betas = []
        betasperc = []
        acc = []
        Cbest = []
        l1best = []
        for train_idx, test_idx in cv.split(X_final, y_final_log):
            model_log = logmodel.fit(X_final.iloc[train_idx], y_final_log.iloc[train_idx])
            acc.append(model_log.score(X_final.iloc[test_idx], y_final_log.iloc[test_idx]))
            clf = model_log.named_steps['logisticregressioncv']
            betas.append(clf.coef_.ravel()) #.ravel()
            betasperc.append((clf.coef_.ravel() != 0).astype(int)) # .ravel()
            Cbest.append(clf.C_)
            l1best.append(clf.l1_ratio_)
        betas = np.array(betas)

        logmodel.fit(X_final, y_final_log)
        clf_final = logmodel.named_steps['logisticregressioncv']
        cv_metrics_log.append({"Variable": v, "Accuracy": acc_cv, "Acc_perm": cv_results_log, "Sens": sens_cv, "Spec": spec_cv, 
                               "pval": pval_log, "acc_CV": acc, "Betas": list(X_final.columns), "Betas%": sum(betasperc)*10,
                               "Betas_mean": np.nanmean(np.where(betas == 0, np.nan, betas), axis=0), "Betas_std": np.nanstd(np.where(betas == 0, np.nan, betas), axis=0), 
                               'Betas_final': clf_final.coef_, 'C_best': Cbest, 'C_best_final': clf_final.C_, 'L1_best': l1best, "l1_ratio_final": clf_final.l1_ratio_})
        # cv_metrics_log.append({"Variable": v, "Accuracy": cv_results_log, 
        #                        "pval": pval_log, "acc_CV": acc, "Betas": list(X_final.columns), "Betas%": sum(betasperc)*10,
        #                        "Betas_mean": np.nanmean(np.where(betas == 0, np.nan, betas), axis=0), "Betas_std": np.nanstd(np.where(betas == 0, np.nan, betas), axis=0), 
        #                        'Betas_final': clf_final.coef_, 'C_best': Cbest, 'C_best_final': clf_final.C_, 'L1_best': l1best, "l1_ratio_final": clf_final.l1_ratio_})
        
        
        
        df_plot = pd.DataFrame({"Prob_high": y_prob, "Group": y_final_log})
        
        palette = {"0": "#2B6CB0", "1": "#E76F51"}
        
        plt.figure(figsize=(6,5.5))
        ax = sns.boxplot(data=df_plot, x="Group", y="Prob_high", palette=palette, width=0.5, showfliers=False, 
                         boxprops=dict(linewidth=2), whiskerprops=dict(linewidth=2), capprops=dict(linewidth=2), medianprops=dict(linewidth=2.5))
        sns.stripplot(data=df_plot, x="Group", y="Prob_high", color="black", alpha=0.35, jitter=0.15, size=4)
        plt.axhline(0.5, linestyle="--", color="red", linewidth=2)
        plt.ylabel("Predicted probability\nLOW <-----------------> HIGH\nTERTIL                      TERTIL", fontsize=25)
        plt.xlabel("")
        plt.ylim([0, 1])
        plt.xticks([0, 1], ["True low\ntertil", "True high\ntertil"], fontsize=25)
        # plt.title(v + " model decision", fontsize=20)
        plt.yticks(fontsize=23)
        sns.despine()
        plt.tight_layout()
        plt.savefig(join(savedir, v +"_model_decision_COND_2.png"))
        

# cv_metrics_df = pd.DataFrame(cv_metrics).set_index("Variable")
# cv_metrics_df.to_excel(join(savedir, "linear_model_summary_10f_" + str(n_permut) + "_new.xlsx"))
cv_metrics_log_df = pd.DataFrame(cv_metrics_log).set_index("Variable")
cv_metrics_log_df.to_excel(join(savedir, "logistic_model_summary_10f_" + str(n_permut) + "_elastic_COND_2.xlsx"))

cv_metrics_log_df = pd.DataFrame(cv_metrics_log).set_index("Variable")
cv_metrics_log_df.to_excel(join(savedir, "logistic_model_summary_10f_" + str(n_permut) + "_" + v + ".xlsx"))
