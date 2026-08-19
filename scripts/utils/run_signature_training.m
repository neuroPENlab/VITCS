function run_signature_training(basedir, CSp_paths, CSm_paths, output_dir, varargin)
%   Train a VITCS-family SVM signature with 10-fold CV.
%
%   RUN_VITCS_TRAINING(basedir, CSp_file, CSm_file, output_dir)
%   RUN_VITCS_TRAINING(..., 'run_sensitivity_analysis', true)
%
%   Shared training routine used for the main VITCS model (all
%   acquisition trials) and the stage-specific VITCS-early / VITCS-late
%   models (first/last five trials only) - see Methods, "Brain
%   signatures of early and late threat acquisition": "The VITCS-early
%   model was trained exclusively on the first five CS+ and CS- trials
%   during threat acquisition, whereas the VITCS-late model was trained
%   on the last five CS+ and CS- trials [...] performance was broadly
%   similar to that of the signature trained using all trials" - i.e.
%   the same training/CV procedure applies to all three models; only
%   the input contrast images differ.
%
%   INPUTS
%       basedir     - project root (same BASEDIR used by the caller)
%       CSp_paths    - cell array with all CS+ contrast paths
%       CSm_paths    - cell array with all CS- contrast paths
%       output_dir  - directory to write this model's outputs to
%
%   NAME-VALUE ARGS
%       'new_10fold_CV' (default false) - train de SVM with new folds. 
%       Only set to true for new analysis. If false, expects 10fold_CV.mat 
%       to already exist under output_dir/.
%       'run_sensitivity_analysis' (default false) - also run the C =
%           0.01/0.1/10 regularization sensitivity analysis. Only set
%           to true for the main VITCS model (Supplementary Table 2);
%           this was not repeated for the early/late variants.
%
%   Expects training_data.mat to already exist under basedir/data/.
%   
%   Dependencies: CANlab Core Tools (fmri_data, predict,
%                 canlab_pattern_similarity)

p = inputParser;
addParameter(p, 'new_10fold_CV', false, @islogical);
addParameter(p, 'run_sensitivity_analysis', false, @islogical);
parse(p, varargin{:});

new_10fold_CV = p.Results.new_10fold_CV;
run_sensitivity_analysis = p.Results.run_sensitivity_analysis;

if ~exist(output_dir, 'dir'); mkdir(output_dir); end

%% Paths
datadir = fullfile(basedir, 'data');
maskdir = fullfile(datadir, 'brainmask.nii');

%% Load training data and 10-fold CV assignment (if false)
tr_set = load(fullfile(datadir, 'training_data.mat')).tr_set;
n_tr_set = sum(tr_set);

training_data = fmri_data([CSp_paths(tr_set), CSm_paths(tr_set)], maskdir);
training_data.Y = [ones(sum(tr_set), 1); -ones(sum(tr_set), 1)];

if new_10fold_CV
    subject_folds = crossvalind('Kfold', n_tr_set, 10);
    sample_folds = [subject_folds, subject_folds];
    save(fullfile(output_dir, '10fold_CV.mat'), 'sample_folds');
else
    sample_folds = load(fullfile(output_dir, '10fold_CV.mat')).sample_folds;
end

%% Train (C = 1) and save the unthresholded weight map
[~, stats_CV_10f] = predict(training_data, 'algorithm_name', 'cv_svm', ...
    'nfolds', sample_folds, 'C', 1, 'error_type', 'mcr', 'dist_from_hyperplane_xval');

% Model performance and ROC plot
figure(1)
rp = roc_plot(stats_CV_10f.dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');
title('ROC plot 10-fold CV (C=1)')

sig = stats_CV_10f.weight_obj;
sig.fullpath = fullfile(savedir, 'VITCS_unthresholded_10foldCV.nii');
write(sig);

% Cohen's D
dif_xval_dist = stats_CV_10f.dist_from_hyperplane_xval(1:n_tr_set ...
    ) - stats_CV_10f.dist_from_hyperplane_xval(n_tr_set+1:end);
d_cv = mean(dif_xval_dist)/std(dif_xval_dist);

fprintf(['10-fold CV misclassification rate (C=1): %.4f; accuracy: %.4f; sensitivity: %.4f; ' ...
    'specificity: %.4f; p-value: %.4f; Cohens D: %.4f\n'], ...
    stats_CV_10f.error_obj.mcr, rp.accuracy, rp.sensitivity, rp.specificity, rp.accuracy_p, d_cv);

% Save cross-validated distance-from-hyperplane values for the ROC figure
xval_dist_C1 = stats_CV_10f.dist_from_hyperplane_xval;
outcome_C1 = training_data.Y == 1;
save(fullfile(savedir, 'VITCS_roc_inputs.mat'), 'xval_dist_C1', 'outcome_C1');

%% Optional: Regularization sensitivity analysis (Supplementary Table 2)
if run_sensitivity_analysis
    C_values = [0.01, 0.1, 1, 10];   % C=1 included so it appears as a row too, alongside 0.01/0.1/10
    n_C = numel(C_values);
 
    classifier_label = strings(n_C, 1);
    accuracy = nan(n_C, 1);
    accuracy_se = nan(n_C, 1);
    cosine_sim_to_C1 = nan(n_C, 1);
 
    for i = 1:n_C
        C_val = C_values(i);
        classifier_label(i) = sprintf('SVM (C=%s)', num2str(C_val));
 
        if C_val == 1
            % Already trained above - reuse stats_CV_10f/sig instead of
            % re-running predict().
            stats_this_C = stats_CV_10f;
            sig_this_C = sig;
        else
            [~, stats_this_C] = predict(training_data, 'algorithm_name', 'cv_svm', ...
                'nfolds', sample_folds, 'C', C_val, 'error_type', 'mcr', ...
                'dist_from_hyperplane_xval');
            sig_this_C = stats_this_C.weight_obj;
        end
 
        % Accuracy (+/- SE) via forced-choice ROC on the CV distances,
        % same approach as Table 1 (see 04_test_set_reversal.m).
        rp = roc_plot(stats_this_C.dist_from_hyperplane_xval, training_data.Y == 1, ...
            'threshold', 'pairedobservations');
        accuracy(i) = rp.accuracy;
        accuracy_se(i) = rp.accuracy_se;
 
        cosine_sim_to_C1(i) = canlab_pattern_similarity(sig.dat, sig_this_C.dat, 'cosine_similarity');
    end
 
    sensitivity_table = table(classifier_label, accuracy, accuracy_se, cosine_sim_to_C1, ...
        'VariableNames', {'classifier', 'accuracy', 'accuracy_se', 'cosine_similarity_to_C1'});
 
    writetable(sensitivity_table, fullfile(output_dir, 'supplementary_table2_C_sensitivity.csv'));
    save(fullfile(output_dir, 'supplementary_table2_C_sensitivity.mat'), 'sensitivity_table');
    fprintf('Sensitivity analysis')
    disp(sensitivity_table);
end

end