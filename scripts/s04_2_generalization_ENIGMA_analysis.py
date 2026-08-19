#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_analysis_ENIGMA.py
@author: Angels Calvet-Mirabent

Compute VITCS (and comparison signature) classification accuracy across
the 26 harmonized datasets of the ENIGMA-Anxiety Fear Conditioning
Group, overall and broken down by unconditioned stimulus (US) modality.

From Methods: "Model generalizability was evaluated using 26
independent datasets from the ENIGMA-Anxiety FC Group. [...] resulting
in a final sample of 26 datasets with a total N = 1,898 (Table 2)."

From Results: Reddan-Threat achieved 75% mean accuracy overall (78% in
electric-shock datasets, n = 1,504; 60% in auditory-US datasets, n =
344; 60% in the thermal-US dataset, n = 50); Liu-SUITAS achieved 86%
overall (88% electric shock, 79% auditory, 74% thermal).

Reads the pattern-expression table produced by 04_validation_ENIGMA.m
(pattern_expression_ENIGMA_all_signatures.xlsx).
"""

from os.path import join
import pandas as pd

#%% --- User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>'  # <-- EDIT THIS, same as other scripts
savedir = join(basedir, 'results', 'VITCS_ENIGMA_generalization') # <-- EDIT THIS, if necessary

pattern_exp_path = join(savedir, 'pattern_expression_ENIGMA_all_signatures.xlsx')

# --- Final set of 26 datasets (confirmed; matches Table 2, N = 1,898) -------
# 'dataset_num' identifiers refer to the internal numbering of the original 43 ENIGMA-Anxiety FC 
# datasets, before the >=30-participants and experimental-design exclusions described in Methods.
FINAL_DATASET_NUMS = [2, 9, 10, 12, 13, 14, 15, 18, 19, 22, 23, 24, 25, 26,
                       28, 30, 31, 32, 33, 36, 38, 39, 40, 41, 42, 43]
assert len(FINAL_DATASET_NUMS) == 26, "Expected exactly 26 datasets (see Methods / Table 2)"

#%% --- Signatures to evaluate (must match column names written by the s04_generalization_ENIGMA.m script) ---
SIGNATURE_NAMES = ['VITCS', 'VITCS_early', 'VITCS_late', 'Reddan_Threat', 'Liu_SUITAS']

# US modality coding.
# US_type is coded 0 = electric shock, 1 = auditory: the thermal-US dataset was intentionally left as NaN 
# in the shared metadata (not a missing-data artifact), so treating NaN as 'thermal' here is correct.
US_MODALITY_MAP = {0: 'electric_shock', 1: 'auditory'}
US_MODALITY_NAN_FALLBACK = 'thermal'

#%% --- Load data and apply the confirmed 26-dataset filter --------------------
data = pd.read_excel(pattern_exp_path, index_col=0)
data = data[data['dataset_num'].isin(FINAL_DATASET_NUMS)]
assert data['dataset'].nunique() == 26, f"Expected 26 unique datasets after filtering, found {data['dataset'].nunique()}"
assert len(data) == 1898, f"Expected N = 1,898 after filtering, found N = {len(data)}"

#%% --- US modality label per participant ---------------------------------------
data['us_modality'] = data['US_type'].map(US_MODALITY_MAP)
data.loc[data['US_type'].isna(), 'us_modality'] = US_MODALITY_NAN_FALLBACK
 
#%% --- Accuracy per signature, overall and by US modality ----------------------
accuracy_rows = []
for sig_name in SIGNATURE_NAMES:
    if sig_name not in data.columns:
        print(f"WARNING: column '{sig_name}' not found in pattern expression table - skipping.")
        continue
 
    # As the contrast analysed is CS+>CS-, correct if pattern expression > 0
    row = {'signature': sig_name, 'n_overall': len(data), 'accuracy_overall': float((data[sig_name] > 0).mean()) * 100,}
    for modality in data['us_modality'].unique():
        subset = data.loc[data['us_modality'] == modality, sig_name]
        row[f'n_{modality}'] = len(subset)
        row[f'accuracy_{modality}'] = float((subset > 0).mean()) * 100
    accuracy_rows.append(row)
 
accuracy_table = pd.DataFrame(accuracy_rows).set_index('signature')
accuracy_table.to_csv(join(savedir, 'ENIGMA_accuracy_by_signature_and_modality.csv'))
print(accuracy_table)
 
# --- VITCS accuracy per each dataset N separately, (Table-2-style summary) -----------
dataset_summary = data.groupby('dataset').agg(
    N=('VITCS', 'size'),
    VITCS_accuracy=('VITCS', lambda values: float((values > 0).mean()) * 100),
)
dataset_summary.to_csv(join(savedir, 'ENIGMA_dataset_summary.csv'))
print(dataset_summary)



