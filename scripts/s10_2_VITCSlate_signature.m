%% s10_2_VITCSlate_signature.m
% -------------------------------------------------------------------
% Train and validate VITCS-late, a stage-specific variant of VITCS trained 
% exclusively on the last five CS+ and CS- trials of the threat acquisition 
% phase, to examine the temporal dynamics of threat learning.
%
% From Methods: "Given the relevance of temporal dynamics in neural responses 
% during human threat conditioning [...], we developed two complementary 
% stage-specific predictive models. The VITCS-early model was trained 
% exclusively on the first five CS+ and CS- trials during threat acquisition, 
% whereas the VITCS-late model was trained on the last five CS+ and CS- trials. 
% As detailed in the Supplementary Information, performance was broadly similar 
% to that of the signature trained using all trials."
%
% This script runs the full VITCS-late pipeline, reusing the same
% shared routines as the main VITCS model (see s02, s03_1, s03_2, s05):
%   (1) training with 10-fold CV on the late-trial contrast images 
%       from the Training Set,
%   (2) validation on the independent Test Set (acquisition and
%       reversal contrasts),
%   (3) out-of-fold pattern expression across the full sample, and
%   (4) bootstrap feature-stability analysis.
%
% To run ENIGMA generalization, mediation and anxiety risk analyses:
%   (1) s04_1_generalization_ENIGMA.m and s04_2_generalization_ENIGMA_analysis.py
%       with SIGNATURE = 'VITCS_late'
%   (2) s07_mediation_analysis.m with SIGNATURE = 'VITCS_late'
%   (3) s08_anxiety_risk_analysis.py with SIGNATURE = 'VITCS_late'
%
% Dependencies: CANlab Core Tools (fmri_data, predict, roc_plot,
%               canlab_pattern_similarity), Spider Toolbox
% -------------------------------------------------------------------
clear; clc;
addpath('utils');

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
contrastdir = '<PATH_TO_CONTRASTS>';   % <-- EDIT THIS
contrast_subpath = fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL'); % <-- EDIT IF YOUR FOLDER STRUCTURE DIFFERS
savedir = fullfile(basedir, 'results', 'VITCS_late_results');   % <-- if necessary, EDIT THIS

contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));

% For VITCS-late development and stability analysis
CSp_late_paths = fullfile(contrastdir, list_subj, contrast_subpath, '<CS+late_contrast_name>.nii'); % <-- EDIT contrast name
CSm_late_paths = fullfile(contrastdir, list_subj, contrast_subpath, '<CS-late_contrast_name>.nii'); % <-- EDIT contrast name

% For VITCS-late validation
contrast_files_test = {{'<name_CS+_file>'; '<name_CS-_file>'}, ...
    {'<name_newCS+_file>'; '<name_newCS-_file>'}};     % <-- EDIT THIS
contrast_names_test = {{'CS+', 'CS-'}, {'newCS+', 'newCS-'}};
% 'CS+'/'CS-'       -> acquisition (Conditioning) contrasts
% 'newCS+'/'newCS-' -> reversal contrasts

% For pattern expression calculation
contrast_files = {'<name_CS+_file>'; '<name_CS-_file>'};
contrast_names = {'CS+', 'CS-'};

%% Train the VITCS-late (last five acquisition trials)
% Run training with predefined folds for the 10-fold CV, 
% to define new ones use 'new_10fold_CV', true. 
run_signature_training(basedir, CSp_late_paths, CSm_late_paths, savedir, 'VITCS-late')

%% Evaluate VITCS-late model on the Test Set
res_VITCSearly  = run_test_set_validation(basedir, contrastdir, contrast_subpath, contrast_files_test, ...
    contrast_names_test, fullfile(savedir, 'VITCS_unthresholded_10foldCV.nii'), ...
    fullfile(savedir, 'VITCS_roc_inputs.mat'), savedir, 'VITCS-late');

%% VITCS-late pattern expression for CS+ and CS- across the full sample
run_full_sample_xval_pattern_expression(basedir, contrastdir, contrast_subpath, ...
    contrast_files, contrast_names, savedir, savedir)

%% Bootstrap the VITCS-late model (using the training set)
run_bootstrap_feature_stability(basedir, CSp_late_paths, CSm_late_paths, ...
    fullfile(savedir, 'reliable_anatomy'))
