#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Saül Pascual-Diaz"
__institution__ = "University of Barcelona"
__date__ = "2025/06/08"
__version__ = "1"
__status__ = "Stable"

"""
cytof_physical_qol_model.py

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
from sklearn.linear_model import LassoCV, RidgeCV, ElasticNetCV, LogisticRegression, LinearRegression, LogisticRegressionCV
from sklearn.model_selection import KFold, StratifiedKFold, permutation_test_score, cross_val_score
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
    basedir = join(subbase, 'results', 'final_brainmask')
    savedir = join(basedir, 'Mult_log_regression', 'PATTERN_EXPRESSION_xval', 'feature_selection_method')
    
    # patexp = pd.read_excel(join(basedir, '2_SVM_results_stai', 'pat_exp_all_data_xval.xlsx'), index_col=0)
    # patexp = pd.read_excel(join(basedir, '1_sig_evaluation', 'pat_exp_reddan.xlsx'), index_col=0)
    # patexp.columns = patexp.columns.str.replace('reddan_', '')
    patexp = pd.read_excel(join(basedir, '1_sig_evaluation', 'pat_exp_SUITAS.xlsx'), index_col=0)
    patexp.columns = patexp.columns.str.replace('suitas_', '')

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
        # df_filtered = df_filtered.loc[:, ['CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate', v]]
    
        # # Run pipeline
        # freqs = bootstrap_selection_vif(
        #     df_filtered,
        #     target_col=v,
        #     vif_thresh=10.0,
        #     n_bootstraps=200,
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

            # X_final = add_constant(df_filtered[stable_vars])
            # y_final = df_filtered[v]
            # model = sm.OLS(y_final, X_final).fit()
            # print("\nFINAL MODEL SUMMARY\n", model.summary())
    
            # # Optional: save coefficients
            # # model.params.to_csv(join(savedir, v + "_final_model_coefficients.csv"))
            # summary_df = pd.DataFrame({
            #     "coef": model.params,
            #     "stderr": model.bse,
            #     "tval": model.tvalues,
            #     "pval": model.pvalues,
            #     "ci_lower": model.conf_int()[0],
            #     "ci_upper": model.conf_int()[1]
            # })
            # summary_df.to_excel(join(savedir, v + "_final_model_coefficients.xlsx"))
            # model_info = pd.DataFrame({
            #     "rsquared": [model.rsquared],
            #     "rsquared_adj": [model.rsquared_adj],
            #     "fvalue": [model.fvalue],
            #     "f_pval": [model.f_pvalue],
            #     "aic": [model.aic],
            #     "bic": [model.bic],
            #     "nobs": [model.nobs]
            # })
            # model_info.to_excel(join(savedir, v + "_final_model_info.xlsx"))
    
            # # Optional: plot
            # predictor = stable_vars[0]
            # sns.regplot(x=df_filtered[predictor], y=y_final)
            # plt.title(f"Effect of {predictor} on {v}")
            # plt.xlabel(predictor)
            # plt.ylabel(v)
            # plt.tight_layout()
            # plt.savefig(join(savedir, v + ".png"), dpi=300)
            # plt.show()
        # else:
        #     print("No predictors passed the stability threshold.")
        
        # Linear Regression Model WITHOUT FEATURE SELECTION
        print('Linear Regression Model with permutation')
        df_filtered = df_filtered.dropna()
        X_final = add_constant(df_filtered.iloc[:,:-1])
        y_final = df_filtered.loc[:,v]
        
        cv = KFold(n_splits=10, shuffle=True, random_state=42)
        
        # grid de alphas (equivalente a C)
        alphas = np.logspace(-3, 1, 10)
        l1_ratios = [0.1, 0.5, 0.7, 0.9, 1]
        
        # # LASSO (L1)
        # print('Lasso Regression with permutation')
        # lasso = make_pipeline(StandardScaler(), LassoCV(alphas=alphas, cv=5, max_iter=5000))
        # cv_r2_lasso, perm_lasso, pval_lasso = permutation_test_score(lasso, X_final, y_final, cv=cv, scoring="r2",
        #                                                              n_permutations=n_permut, random_state=42, n_jobs=1)
        # r2_lasso = []
        # betas_lasso = []
        # betas_lassoperc = []
        # alphas_lasso = []
        # for train_idx, test_idx in cv.split(X_final, y_final):
        #     model1 = lasso.fit(X_final.iloc[train_idx], y_final.iloc[train_idx])
        #     r2_lasso.append(model1.score(X_final.iloc[test_idx], y_final.iloc[test_idx]))
        #     betas_lasso.append(model1.named_steps['lassocv'].coef_)
        #     betas_lassoperc.append((model1.named_steps['lassocv'].coef_!=0).astype(int))
        #     alphas_lasso.append(model1.named_steps['lassocv'].alpha_)
        
        # betas_lasso = np.array(betas_lasso)
        
        # # final model
        # lasso_final = lasso.fit(X_final, y_final)
        # final_coef_lasso = lasso_final.named_steps['lassocv'].coef_
        
        
        # # RIDGE (L2)
        # print('Ridge Regression with permutation')
        # ridge = make_pipeline(StandardScaler(), RidgeCV(alphas=alphas, cv=5))
        # cv_r2_ridge, perm_ridge, pval_ridge = permutation_test_score(ridge, X_final, y_final, cv=cv, scoring="r2",
        #                                                              n_permutations=n_permut, random_state=42, n_jobs=1)
        # r2_ridge = []
        # betas_ridge = []
        # betas_ridgeperc = []
        # alphas_ridge = []
        # for train_idx, test_idx in cv.split(X_final, y_final):
        #     model2 = ridge.fit(X_final.iloc[train_idx], y_final.iloc[train_idx])
        #     r2_ridge.append(model2.score(X_final.iloc[test_idx], y_final.iloc[test_idx]))
        #     betas_ridge.append(model2.named_steps['ridgecv'].coef_)
        #     betas_ridgeperc.append((model2.named_steps['ridgecv'].coef_!=0).astype(int))
        #     alphas_ridge.append(model2.named_steps['ridgecv'].alpha_)
        
        # betas_ridge = np.array(betas_ridge)
        
        # # final model
        # ridge_final = ridge.fit(X_final, y_final)
        # final_coef_ridge = ridge_final.named_steps['ridgecv'].coef_
        
        
        # LINEAR REGRESSION
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

        
        
        
        # ELASTIC NET
        print('Elastic Net Regression with permutation')
        elastic = make_pipeline(StandardScaler(), ElasticNetCV(alphas=alphas, l1_ratio=l1_ratios, cv=5, max_iter=5000))
        cv_r2_elastic, perm_elastic, pval_elastic = permutation_test_score(elastic, X_final, y_final, cv=cv, scoring="r2",
                                                                           n_permutations=n_permut, random_state=42, n_jobs=1)
        r2_elastic = []
        betas_elastic = []
        betas_elasticperc = []
        alphas_elastic = []
        l1_elastic = []
        for train_idx, test_idx in cv.split(X_final):
            model3 = elastic.fit(X_final.iloc[train_idx], y_final.iloc[train_idx])
            r2_elastic.append(model3.score(X_final.iloc[test_idx], y_final.iloc[test_idx]))
            betas_elastic.append(model3.named_steps['elasticnetcv'].coef_)
            betas_elasticperc.append((model3.named_steps['elasticnetcv'].coef_!=0).astype(int))
            alphas_elastic.append(model3.named_steps['elasticnetcv'].alpha_)
            l1_elastic.append(model3.named_steps['elasticnetcv'].l1_ratio_)
        
        betas_elastic = np.array(betas_elastic)
        
        # final model
        scores_elastic = cross_val_score(elastic, X_final, y_final, cv=cv, scoring='r2')
        plt.plot(scores_elastic, marker='o')
        plt.axhline(0, linestyle='--', color='red')
        plt.axhline(scores_elastic.mean(), color='yellow')
        plt.axhline(perm_elastic.mean(), color='orange')
        plt.ylabel('Fold R²')
        plt.xlabel('Fold')
        plt.legend(['CV R²', 'chance', 'mean CV R²', 'mean permutation R²'])
        plt.show()
        
        plt.plot(perm_elastic, marker='.')
        plt.axhline(0, linestyle='--', color='red')
        plt.ylabel('Permutation R²')
        plt.xlabel('Permutation')
        plt.show()

        elastic_final = elastic.fit(X_final, y_final)
        final_coef_elastic = elastic_final.named_steps['elasticnetcv'].coef_
        
        # cv_metrics.append({"Variable": v, "R2_lasso": cv_r2_lasso, "pval_lasso": pval_lasso, "alphas_lasso": alphas_lasso,
        #                    "betas_lasso_mean": np.nanmean(np.where(betas_lasso == 0, np.nan, betas_lasso), axis=0),
        #                    "betas_lasso_std": np.nanstd(np.where(betas_lasso == 0, np.nan, betas_lasso), axis=0), 
        #                    "betas_lasso%": sum(betas_lassoperc)*10, "final_coef_lasso": final_coef_lasso,
        #                    "R2_ridge": cv_r2_ridge, "pval_ridge": pval_ridge, "alphas_ridge": alphas_ridge,
        #                    "betas_ridge_mean": np.nanmean(np.where(betas_ridge == 0, np.nan, betas_ridge), axis=0),
        #                    "betas_ridge_std": np.nanstd(np.where(betas_ridge == 0, np.nan, betas_ridge), axis=0), 
        #                    "betas_ridge%": sum(betas_ridgeperc)*10, "final_coef_ridge": final_coef_ridge,
        #                    "R2_elastic": cv_r2_elastic, "pval_elastic": pval_elastic, "alphas_elastic": alphas_elastic,
        #                    "betas_elastic_mean": np.nanmean(np.where(betas_elastic == 0, np.nan, betas_elastic), axis=0),
        #                    "betas_elastic_std": np.nanstd(np.where(betas_elastic == 0, np.nan, betas_elastic), axis=0), 
        #                    "betas_elastic%": sum(betas_elasticperc)*10, "final_coef_elastic": final_coef_elastic})
        cv_metrics.append({"Variable": v, "R2_elastic": cv_r2_elastic, "pval_elastic": pval_elastic, "alphas_elastic": alphas_elastic,
                           "betas_elastic_mean": np.nanmean(np.where(betas_elastic == 0, np.nan, betas_elastic), axis=0),
                           "betas_elastic_std": np.nanstd(np.where(betas_elastic == 0, np.nan, betas_elastic), axis=0), 
                           "betas_elastic%": sum(betas_elasticperc)*10, "final_coef_elastic": final_coef_elastic})
        
cv_metrics_df = pd.DataFrame(cv_metrics).set_index("Variable")
cv_metrics_df.to_excel(join(savedir, "linear_model_summary_10f_" + str(n_permut) + "_all_DATA_elastic_ALL.xlsx"))

cv_metrics_df = pd.DataFrame(cv_metrics).set_index("Variable")
cv_metrics_df.to_excel(join(savedir, "linear_model_summary_10f_" + str(n_permut) + ".xlsx"))

