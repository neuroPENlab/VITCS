%% s02_train_VITCS_signature.m
% -------------------------------------------------------------------
% Train the VITCS (Visually Induced Threat Conditioning Signature)
% classifier and evaluate its cross-validated performance.
%
% From Methods: "We developed our whole-brain predictive model of
% threat conditioning using support vector machines (SVMs) implemented
% in the CANlab toolbox. [...] Within the Training Set (n = 138), the
% predictive model was trained using CS+ and CS- contrast images from
% the threat acquisition phase [...]. We used 10-fold cross-validation
% to estimate within-subject classification accuracy."
%
% Also reproduces Supplementary Table 2 ("Sensitivity analysis of the
% VITCS model across alternative SVM regularization parameters",
% C = 0.01, 0.1, 1, 10).
%
% Dependencies: CANlab Core Tools (fmri_data, predict, roc_plot,
%               canlab_pattern_similarity), Spider Toolbox
% -------------------------------------------------------------------
clear; clc;
addpath('utils');

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
datadir = fullfile(basedir, 'data');   % <-- if necessary, EDIT THIS
savedir = fullfile(basedir, 'results', 'VITCS_development');   % <-- if necessary, EDIT THIS
list_subj = {}; % <-- EDIT THIS, same as s01_train_test_split.m: list of subjects to include

CSp_paths = {'<PATHS_TO_CS+_CONTRAST_DATA>'}; % <-- EDIT THIS: cell array with all CS+ contrast files
CSm_paths = {'<PATHS_TO_CS-_CONTRAST_DATA>'}; % <-- EDIT THIS: cell array with all CS- contrast files

contrastdir = '/Users/acalvet/Documents/MVPA_FISAX/DATA/contrasts_brainmask';
contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));
CSp_paths = fullfile(contrastdir, list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0011_mask.nii');
CSm_paths = fullfile(contrastdir, list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0012_mask.nii');

%% Train the main VITCS model (all acquisition trials)
% Run VITCS training with sensitivity analysis and predefined folds for the
% 10-fold CV, to define new ones use 'new_10fold_CV', true. 
run_signature_training(basedir, CSp_paths, CSm_paths, savedir, 'run_sensitivity_analysis', true)