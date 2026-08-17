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

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
datadir = fullfile(basedir, 'data');   % <-- if necessary, EDIT THIS
savedir = fullfile(basedir, 'results', 'VITCS_development');   % <-- if necessary, EDIT THIS
if ~exist(savedir, 'dir'); mkdir(savedir); end
list_subj = {}; % <-- EDIT THIS, same as s01_train_test_split.m: list of subjects to include

CSp_paths = '<PATHS_TO_CS+_CONTRAST_DATA>'; % <-- EDIT THIS: cell array with all CS+ contrast files
CSm_paths = '<PATHS_TO_CS-_CONTRAST_DATA>'; % <-- EDIT THIS: cell array with all CS- contrast files
maskdir = fullfile(datadir, 'brainmask.nii');

% If true, load the exact 10-folds indices used in the manuscript
% (provided in this repository). Set to false only if you want to draw new
% folds (this will NOT reproduce exacly the published results).
USE_PUBLISHED_10foldsCV = true;

%% Load subject contrast paths and the train/test split
tr_set = load(fullfile(datadir, 'training_data.mat')).tr_set;
ts_set = load(fullfile(datadir, 'test_data.mat')).ts_set;
n_tr_set = sum(tr_set);

training_data = fmri_data([CSp_paths(tr_set), CSm_paths(tr_set)], maskdir);
training_data.Y = [ones(sum(tr_set), 1); -ones(sum(tr_set), 1)];

test_data = fmri_data([CSp_paths(ts_set), CSm_paths(ts_set)], maskdir);
test_data.Y = [ones(sum(ts_set), 1); -ones(sum(ts_set), 1)];

%% 10-fold cross-validation folds

if USE_PUBLISHED_10foldsCV
    sample_folds = load(fullfile(datadir, '10fold_CV.mat')).sample_folds;
else
    subject_folds = crossvalind('Kfold', n_tr_set, 10);
    sample_folds = [subject_folds, subject_folds];
    save(fullfile(datadir, '10fold_CV.mat'), 'sample_folds');
end

%% Train the primary VITCS classifier (C = 1) 
[~, stats_CV_10f] = predict(training_data, 'algorithm_name', 'cv_svm', ...
    'nfolds', sample_folds, 'C', 1, 'error_type', 'mcr', 'dist_from_hyperplane_xval');

% Model performance and ROC plot
figure(1)
roc_plot(stats_CV_10f.dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');
title('ROC plot 10-fold CV (C=1)')

orthviews(stats_CV_10f.weight_obj); % For sanity check
sig = stats_CV_10f.weight_obj;
sig.fullpath = fullfile(savedir, 'VITCS_unthresholded_10foldCV.nii');
write(sig);

fprintf('10-fold CV misclassification rate (C=1): %.4f\n', stats_CV_10f.error_obj.mcr);

%% Regularization sensitivity analysis (Supplementary Table 2)
C_values = [0.01, 0.1, 10];
stats_by_C = struct();

for i = 1:numel(C_values)
    C_val = C_values(i);
    field_name = sprintf('C_%s', strrep(num2str(C_val), '.', 'p'));
    [~, stats_by_C.(field_name)] = predict(training_data, 'algorithm_name', 'cv_svm', ...
        'nfolds', sample_folds, 'C', C_val, 'error_type', 'mcr', 'dist_from_hyperplane_xval');
    
    % Model performance and ROC plot
    figure(i+1)
    roc_plot(stats_by_C.(field_name).dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');
    title(sprintf('ROC plot 10-fold CV (C=%s)', num2str(C_val)))
end

% Cosine similarity between the primary (C=1) weight map and each alternative
% regularization weight map (reported in Supplementary Table 2).
fn = fieldnames(stats_by_C);
for i = 1:numel(fn)
    other_sig = stats_by_C.(fn{i}).weight_obj;
    sim = canlab_pattern_similarity(sig.dat, other_sig.dat, 'cosine_similarity');
    fprintf('Cosine similarity C=%s vs. C=1: %.6f\n', fn{i}, sim);
end

%% Save cross-validated distance-from-hyperplane values for the ROC figure
xval_dist_C1 = stats_CV_10f.dist_from_hyperplane_xval;
outcome_C1 = training_data.Y == 1;
save(fullfile(savedir, 'VITCS_roc_inputs.mat'), 'xval_dist_C1', 'outcome_C1');