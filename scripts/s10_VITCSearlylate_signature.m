%% s10_VITCSearlylate_signature.m
% -------------------------------------------------------------------
% RE-WRITE
%
% From Methods: "....¿??"
%
% Dependencies: CANlab Core Tools (fmri_data, predict, roc_plot,
%               canlab_pattern_similarity), Spider Toolbox
% -------------------------------------------------------------------
clear; clc;
addpath('utils');

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
datadir = fullfile(basedir, 'data');   % <-- if necessary, EDIT THIS
savedir_early = fullfile(basedir, 'results', 'VITCS_early_results');   % <-- if necessary, EDIT THIS
savedir_late = fullfile(basedir, 'results', 'VITCS_late_results');   % <-- if necessary, EDIT THIS
list_subj = {}; % <-- EDIT THIS, same as s01_train_test_split.m: list of subjects to include

CSp_early_paths = {'<PATHS_TO_CS+early_CONTRAST_DATA>'}; % <-- EDIT THIS: cell array with all CS+ contrast files
CSm_early_paths = {'<PATHS_TO_CS-early_CONTRAST_DATA>'}; % <-- EDIT THIS: cell array with all CS- contrast files
CSp_late_paths = {'<PATHS_TO_CS+early_CONTRAST_DATA>'}; % <-- EDIT THIS: cell array with all CS+ contrast files
CSm_late_paths = {'<PATHS_TO_CS-early_CONTRAST_DATA>'}; % <-- EDIT THIS: cell array with all CS- contrast files

contrastdir = '/Users/acalvet/Documents/MVPA_FISAX/DATA/contrasts_brainmask';
contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));
CSp_paths = fullfile(contrastdir, list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0011_mask.nii');
CSm_paths = fullfile(contrastdir, list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0012_mask.nii');

%% Train the VITCS-early and VITCS-late models (all acquisition trials)
% Run training with predefined folds for the 10-fold CV, 
% to define new ones use 'new_10fold_CV', true. 
run_signature_training(basedir, CSp_early_paths, CSm_early_paths, savedir_early)

run_signature_training(basedir, CSp_late_paths, CSm_late_paths, savedir_late)

%% Evaluate VITCS-early and VITCS-late models on the Test Set
res_VITCSearly  = run_test_set_validation(basedir, fullfile(savedir_early, 'VITCS_unthresholded_10foldCV.nii'), ...
    fullfile(savedir_early, 'VITCS_roc_inputs.mat'), savedir_early, 'VITCS-early');

res_VITCSlate  = run_test_set_validation(basedir, fullfile(savedir_late, 'VITCS_unthresholded_10foldCV.nii'), ...
    fullfile(savedir_late, 'VITCS_roc_inputs.mat'), savedir_late, 'VITCS-late');

%% Bootstrap the VITCS-early and VITCS-late models (using the training set)
run_bootstrap_feature_stability(basedir, CSp_early_paths, CSm_early_paths, savedir_early)

run_bootstrap_feature_stability(basedir, CSp_late_paths, CSm_late_paths, savedir_late)