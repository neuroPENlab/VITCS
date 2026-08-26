#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s04_2_generalization_ENIGMA_analysis.py
@author: Angels Calvet-Mirabent

Compute VITCS (and comparison signature) classification accuracy across the 26 harmonized datasets of the 
ENIGMA-Anxiety Fear Conditioning Group, overall and broken down by unconditioned stimulus (US) modality.

From Methods: "Model generalizability was evaluated using 26 independent datasets from the ENIGMA-Anxiety 
FC Group. [...] resulting in a final sample of 26 datasets with a total N = 1,898 (Table 2)."

From Results: Reddan-Threat achieved 75% mean accuracy overall (78% in electric-shock datasets, n = 1,504; 
60% in auditory-US datasets, n = 344; 60% in the thermal-US dataset, n = 50); Liu-SUITAS achieved 86%
overall (88% electric shock, 79% auditory, 74% thermal).

Reads the pattern-expression table produced by 04_validation_ENIGMA.m (pattern_expression_ENIGMA.xlsx).

Run once per signature: set SIGNATURE below and re-run.
"""

from os.path import join
import pandas as pd

#%% --- User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>'  # <-- EDIT THIS, same as other scripts

# --- Final set of 26 datasets (confirmed; matches Table 2, N = 1,898) -------
# 'dataset_num' identifiers refer to the internal numbering of the original 43 ENIGMA-Anxiety FC 
# datasets, before the >=30-participants and experimental-design exclusions described in Methods.
FINAL_DATASET_NUMS = [2, 9, 10, 12, 13, 14, 15, 18, 19, 22, 23, 24, 25, 26,
                       28, 30, 31, 32, 33, 36, 38, 39, 40, 41, 42, 43]
assert len(FINAL_DATASET_NUMS) == 26, "Expected exactly 26 datasets (see Methods / Table 2)"

# ---  Which signature to run mediation for ----------------------------------
SIGNATURE = "VITCS" # <-- EDIT THIS: 'VITCS' | 'Reddan-Threat' | 'Liu-SUITAS' | 'VITCS_early' | 'VITCS_late'

if SIGNATURE == "VITCS":
    pat_exp_path = join(basedir, 'results', 'VITCS_ENIGMA_generalization', 'pattern_expression_ENIGMA_' + SIGNATURE + '.xlsx'); # from 04b + 04d
    savedir = join(basedir, 'results', 'VITCS_ENIGMA_generalization');
elif SIGNATURE == "Reddan-Threat":
    pat_exp_path = join(basedir, 'results', 'comparison_existing_signatures', 'pattern_expression_ENIGMA_' + SIGNATURE + '.xlsx'); # from 04d
    savedir = join(basedir, 'results', 'comparison_existing_signatures');
elif SIGNATURE == "Liu-SUITAS":
    pat_exp_path = join(basedir, 'results', 'comparison_existing_signatures', 'pattern_expression_ENIGMA_' + SIGNATURE + '.xlsx'); # from 04d
    savedir = join(basedir, 'results', 'comparison_existing_signatures');
elif SIGNATURE == "VITCS_early":
    pat_exp_path = join(basedir, 'results', 'VITCS_early_results', 'pattern_expression_ENIGMA_' + SIGNATURE + '.xlsx'); # from 04c
    savedir = join(basedir, 'results', 'VITCS_early_results');
elif SIGNATURE == "VITCS_late":
    pat_exp_path = join(basedir, 'results', 'VITCS_late_results', 'pattern_expression_ENIGMA_' + SIGNATURE + '.xlsx'); # from 04c
    savedir = join(basedir, 'results', 'VITCS_late_results');
else:
    print("That's not a valid signature.")

# US modality coding.
# US_type is coded 0 = electric shock, 1 = auditory: the thermal-US dataset was intentionally left as NaN 
# in the shared metadata (not a missing-data artifact), so treating NaN as 'thermal' here is correct.
US_MODALITY_MAP = {0: 'electric_shock', 1: 'auditory'}
US_MODALITY_NAN_FALLBACK = 'thermal'

#%% --- Load data and apply the confirmed 26-dataset filter --------------------
data = pd.read_excel(pat_exp_path, index_col=0)
data.insert(6, 'dataset_num', 0)
for n, dataset_name in enumerate(data.dataset.unique()):
    data.loc[data['dataset'] == dataset_name, 'dataset_num'] = n+1

data = data[data['dataset_num'].isin(FINAL_DATASET_NUMS)]
assert data['dataset'].nunique() == 26, f"Expected 26 unique datasets after filtering, found {data['dataset'].nunique()}"
assert len(data) == 1898, f"Expected N = 1,898 after filtering, found N = {len(data)}"

#%% --- US modality label per participant ---------------------------------------
data['us_modality'] = data['US_type'].map(US_MODALITY_MAP)
data.loc[data['US_type'].isna(), 'us_modality'] = US_MODALITY_NAN_FALLBACK
 
#%% --- Accuracy per signature, overall and by US modality ----------------------
accuracy_rows = []
if SIGNATURE not in data.columns:
    print(f"WARNING: column '{SIGNATURE}' not found in pattern expression table.")
 
# As the contrast analysed is CS+>CS-, correct if pattern expression > 0
row = {'signature': SIGNATURE, 'n_overall': len(data), 'accuracy_overall': float((data[SIGNATURE] > 0).mean()) * 100,}
for modality in data['us_modality'].unique():
    subset = data.loc[data['us_modality'] == modality, SIGNATURE]
    row[f'n_{modality}'] = len(subset)
    row[f'accuracy_{modality}'] = float((subset > 0).mean()) * 100
accuracy_rows.append(row)
 
accuracy_table = pd.DataFrame(accuracy_rows).set_index('signature').T
accuracy_table.to_csv(join(savedir, 'ENIGMA_' + SIGNATURE + '_accuracy_by_modality.csv'))
print(accuracy_table)

if SIGNATURE == 'VITCS':
    # --- VITCS accuracy per each dataset N separately, (Table-2-style summary) -----------
    dataset_summary = data.groupby('dataset').agg(
        N=('VITCS', 'size'),
        VITCS_accuracy=('VITCS', lambda values: float((values > 0).mean()) * 100),
    )
    dataset_summary.to_csv(join(savedir, 'ENIGMA_' + SIGNATURE+ '_dataset_summary.csv'))
    print(dataset_summary)



