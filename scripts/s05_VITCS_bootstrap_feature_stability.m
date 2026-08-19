%% s05_VITCS_bootstrap_feature_stability.m
% -------------------------------------------------------------------
% Identify brain regions that most reliably contribute to the VITCS
% threat vs. safety classification, using bootstrap resampling.
%
% From Methods: "In order to identify the brain regions that most
% significantly and reliably contributed to the VITCS threat-safety
% classification, we conducted a bootstrap analysis with 5,000
% resamples (with replacement) and applied false discovery rate (FDR)
% correction for thresholding."
%
% From the Supplementary Text ("SVM classification and Bootstrap
% Inference"): voxel-wise two-tailed p-values were computed from the
% bootstrap distribution and thresholded at FDR q < 0.05. Uncorrected
% thresholds (p < .001 and p < .01) are additionally reported for
% visualization purposes.
%
% Dependencies: CANlab Core Tools (fmri_data, predict, threshold, write)
% -------------------------------------------------------------------
clear; clc;
addpath('utils');

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
savedir = fullfile(basedir, 'results', 'VITCS_development');   % <-- if necessary, EDIT THIS
list_subj = {}; % <-- EDIT THIS, same as s01_train_test_split.m: list of subjects to include

CSp_paths = '<PATHS_TO_CS+_CONTRAST_DATA>'; % <-- EDIT THIS: cell array with all CS+ contrast files
CSm_paths = '<PATHS_TO_CS-_CONTRAST_DATA>'; % <-- EDIT THIS: cell array with all CS- contrast files
maskdir = fullfile(datadir, 'brainmask.nii');

%% Bootstrap the VITCS model (using the training set)
run_bootstrap_feature_stability(basedir, CSp_paths, CSm_paths, savedir)