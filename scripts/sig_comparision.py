#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 11:39:56 2025

@author: acalvet
"""
import pandas as pd
from os.path import join
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

base_dir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai'

cos_vits = pd.read_excel(join(base_dir, 'pat_exp_all_data_xval_cosine.xlsx'), index_col=0)
cos_threat = pd.read_excel(join(base_dir, 'pat_exp_all_data_THREAT_cosine.xlsx'), index_col=0)
cos_threat.columns = cos_threat.columns.str.replace('Threat_', '')
cos_wen = pd.read_excel(join(base_dir, 'pat_exp_all_data_WEN_cosine.xlsx'), index_col=0)
cos_wen.columns = cos_wen.columns.str.replace('Wen_', '')

#cos_threat.index == cos_vits.index

for col in cos_vits.columns:
    
    # Linear regression REDDAN vs VITS
    x = cos_threat[col].values.reshape(-1, 1)
    y = cos_vits[col].values
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    r2 = r2_score(y, y_pred)
    
    plt.figure()
    plt.plot(x, y_pred, color='red', label=f'$R^2$ = {r2:.2f}')
    plt.scatter(cos_threat[col], cos_vits[col])
    plt.xlabel('Reddan signature')
    plt.ylabel('VITS')
    plt.title('Reddan vs VITS cosine similatiry in ' + col)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Linear regression WEN vs VITS
    x = cos_wen[col].values.reshape(-1, 1)
    y = cos_vits[col].values
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    r2 = r2_score(y, y_pred)
    
    plt.figure()
    plt.plot(x, y_pred, color='red', label=f'$R^2$ = {r2:.2f}')
    plt.scatter(cos_wen[col], cos_vits[col])
    plt.xlabel('Wen signature')
    plt.ylabel('VITS')
    plt.title('Wen vs VITS cosine similatiry in ' + col)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # Linear regression REDDAN vs WEN
    x = cos_threat[col].values.reshape(-1, 1)
    y = cos_wen[col].values
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    r2 = r2_score(y, y_pred)
    
    plt.figure()
    plt.plot(x, y_pred, color='red', label=f'$R^2$ = {r2:.2f}')
    plt.scatter(cos_threat[col], cos_wen[col])
    plt.xlabel('Reddan signature')
    plt.ylabel('Wen signature')
    plt.title('Reddan vs Wen cosine similatiry in ' + col)
    plt.legend()
    plt.tight_layout()
    plt.show()
