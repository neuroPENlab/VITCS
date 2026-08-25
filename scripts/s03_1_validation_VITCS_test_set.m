%% s03_1_validation_VITCS_test_set.m
% -------------------------------------------------------------------
% Validate the VITCS signature on the independent, held-out Test Set
% (20% of the sample) for both the acquisition (CS+/CS-) and reversal
% (newCS+/newCS-) contrasts.
%
% Computes pattern expression (dot product with the VITCS weight map)
% for each test-set participant, then classification performance
% (accuracy +- SE, sensitivity (CI), specificity (CI), AUC, p-value,
% Cohen's D) via forced-choice ROC analysis. These are the values 
% underlying Table 1.
%
% Dependencies: CANlab Core Tools (fmri_data, canlab_pattern_similarity,
%               roc_plot)
% -------------------------------------------------------------------
clear; clc;
addpath('utils');

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
contrastdir = '<PATH_TO_CONTRASTS>';   % <-- EDIT THIS
contrast_subpath = fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL'); % <-- EDIT IF YOUR FOLDER STRUCTURE DIFFERS

sigdir  = fullfile(basedir, 'results', 'VITCS_development');   % where 02_train_VITCS_signature.m wrote its outputs
savedir = fullfile(basedir, 'results', 'VITCS_validation');   % <-- if necessary, EDIT THIS

contrast_files = {{'<name_CS+_file>'; '<name_CS-_file>'}, ...
    {'<name_newCS+_file>'; '<name_newCS-_file>'}};     % <-- EDIT THIS
contrast_names = {{'CS+', 'CS-'}, {'newCS+', 'newCS-'}};
% 'CS+'/'CS-'       -> acquisition (Conditioning) contrasts
% 'newCS+'/'newCS-' -> reversal contrasts

%% Evaluate VITCS model on the Test Set
results  = run_test_set_validation(basedir, contrastdir, contrast_subpath, contrast_files, ...
    contrast_names, fullfile(sigdir, 'VITCS_unthresholded_10foldCV.nii'), ...
    fullfile(sigdir, 'VITCS_roc_inputs.mat'), savedir, 'VITCS');