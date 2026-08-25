%% s03_2_full_sample_xval_pattern_expression.m
% -------------------------------------------------------------------
% Compute VITCS pattern expression for the FULL sample (N=172, training
% + test subjects together) using a leave-one-fold-out approach for
% training subjects, so that no subject's pattern expression is
% computed from a model that included them in its own training.
%
% For each training-set subject, VITCS expression is computed using the
% weight map from the 10-fold CV fold that LEFT THAT SUBJECT OUT (i.e.
% out-of-fold prediction, same principle as cross-validated accuracy).
% For test-set subjects (never used in any training fold), the full
% trained model is used directly.
%
% Shared input for 07_mediation_analysis.m, 08_anxiety_risk_analysis.py,
% and 09_comparison_existing_signatures.m (Table 4's "Total Sample
% Discrimination" row).
%
% Dependencies: CANlab Core Tools (fmri_data, canlab_pattern_similarity)
% -------------------------------------------------------------------
clear; clc;
addpath('utils');

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
contrastdir = '<PATH_TO_CONTRASTS>';   % <-- EDIT THIS
contrast_subpath = fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL'); % <-- EDIT IF YOUR FOLDER STRUCTURE DIFFERS

sigdir  = fullfile(basedir, 'results', 'VITCS_development');   % where 02_train_VITCS_signature.m wrote its outputs
savedir = fullfile(basedir, 'results', 'VITCS_validation');   % <-- if necessary, EDIT THIS

contrast_files = {'<name_CS+_file>'; '<name_CS-_file>'};     % <-- EDIT THIS
contrast_names = {'CS+', 'CS-'};
% 'CS+'/'CS-'       -> acquisition (Conditioning) contrasts
% 'newCS+'/'newCS-' -> reversal contrasts

%% Main VITCS model
run_full_sample_xval_pattern_expression(basedir, contrastdir, contrast_subpath, ...
    contrast_files, contrast_names, sigdir, sigdir)