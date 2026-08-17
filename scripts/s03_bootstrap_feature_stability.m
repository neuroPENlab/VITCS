%% s03_bootstrap_feature_stability.m
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
% visualization purposes in datasets where no voxels survive whole-brain
% FDR correction (Supplementary Fig. 6).
%
% Dependencies: CANlab Core Tools (fmri_data, predict, threshold, write)
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
datadir = fullfile(basedir, 'data');   % <-- if necessary, EDIT THIS
savedir = fullfile(basedir, 'results', 'VITCS_development');   % <-- if necessary, EDIT THIS
if ~exist(savedir, 'dir'); mkdir(savedir); end
list_subj = {}; % <-- EDIT THIS, same as s01_train_test_split.m: list of subjects to include

CSp_paths = '<PATHS_TO_CS+_CONTRAST_DATA>'; % <-- EDIT THIS: cell array with all CS+ contrast files
CSm_paths = '<PATHS_TO_CS-_CONTRAST_DATA>'; % <-- EDIT THIS: cell array with all CS- contrast files
maskdir = fullfile(datadir, 'brainmask.nii');

%% Load training data 
tr_set = load(fullfile(datadir, 'training_data.mat')).tr_set;

training_data = fmri_data([CSp_paths(tr_set), CSm_paths(tr_set)], maskdir);
training_data.Y = [ones(sum(tr_set), 1); -ones(sum(tr_set), 1)];

%% Bootstrap resampling (5,000 samples) 
[~, stats_boot] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', 1, 'C', 1, ...
    'error_type', 'mcr', 'bootweights', 'bootsamples', 5000);

%% Threshold the bootstrapped weight map 
boot_fdr05  = threshold(stats_boot.weight_obj, .05,  'fdr', 'mask', maskdir);
boot_unc001 = threshold(stats_boot.weight_obj, .001, 'unc', 'mask', maskdir);
boot_unc01  = threshold(stats_boot.weight_obj, .01,  'unc', 'mask', maskdir);

%% Save thresholded maps 
boot_fdr05.fullpath = fullfile(savedir, 'VITCS_bootstrap_fdr05.nii');
write(boot_fdr05, 'thresh');

boot_unc001.fullpath = fullfile(savedir, 'VITCS_bootstrap_unc001.nii');
write(boot_unc001, 'thresh');

boot_unc01.fullpath = fullfile(savedir, 'VITCS_bootstrap_unc01.nii');
write(boot_unc01, 'thresh');