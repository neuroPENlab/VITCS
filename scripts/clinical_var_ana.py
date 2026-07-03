#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 12:34:27 2024

@author: acalvet

Script to analyse clinical data variables
"""
import pandas as pd
from os.path import join
import matplotlib.pyplot as plt
from IPython.display import display

dir_treb = '/Users/acalvet/Documents/MVPA_FISAX'
name_excel = 'Quest_final_dataset.xlsx'
data = pd.read_excel(join(dir_treb, name_excel), index_col=0)

# Variable description
summary = data.describe()
display(summary)

for q in data.columns[2:]:
    n_bins = 50
    plt.figure(figsize=(10, 6))  # Creates a 2x2 grid of subplots with a size of 10x10 inches
    plt.hist(data[q], bins = n_bins, color='#86bf91')
    plt.xlabel(q)
    plt.ylabel('Count')
    
    # BY SEX
    plt.figure(figsize=(10, 6))  # Creates a 2x2 grid of subplots with a size of 10x10 inches
    plt.hist([data[data.Sex == 0][q], data[data.Sex == 1][q]], bins = n_bins, 
             color=['blue', 'green'], label=['Male = ' + str(sum(data[[q, 'Sex']].dropna().Sex==0)), 'Female = ' + str(sum(data[[q, 'Sex']].dropna().Sex==1))], alpha=0.5)
    plt.legend()
    plt.xlabel(q)
    plt.ylabel('Count')
    
    # Boxplot
    plt.figure(figsize = (5,5))
    data.boxplot([q], by = 'Sex', grid = False)
    plt.title(q)
    plt.show()
    plt.rcParams.update({'font.size': 11})
