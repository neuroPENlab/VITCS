function results = run_test_set_validation(basedir, sig_path, roc_inputs_path, output_dir, model_label)
%   Evaluate a VITCS-family signature on the Test Set.
%
%   results = RUN_VITCS_TEST_EVALUATION(basedir, sig_path, ...
%       roc_inputs_path, output_dir, model_label)
%
%   Shared evaluation routine for the main VITCS model and the
%   VITCS-early / VITCS-late variants - see Methods/Supplementary Text:
%   "[VITCS-early] achieved 86% 10-fold cross-validated accuracy, 91%
%   accuracy in the independent Test Set, and 88% accuracy when applied
%   to the reversal-learning phase. The VITCS-late model [...] yielding
%   accuracies of 85%, 94%, and 97%, respectively." I.e. the same
%   evaluation procedure (10-fold CV performance + Test Set performance
%   on both the acquisition and reversal contrasts) is applied to all
%   three models; only the input signature differs.
%
%   INPUTS
%       basedir         - project root
%       sig_path        - path to this model's unthresholded signature
%                          .nii (output of run_VITCS_training.m)
%       roc_inputs_path - path to this model's VITCS_roc_inputs.mat
%                          (10-fold CV distances, also from
%                          run_VITCS_training.m)
%       output_dir      - directory to write this model's evaluation
%                          outputs to
%       model_label     - short string used in filenames, e.g. 'VITCS',
%                          'VITCS_early', 'VITCS_late'
%
%   OUTPUT
%       results - struct with per-participant distances/outcomes for
%                 the acquisition and reversal contrasts (dist_cond,
%                 outcome_cond, dist_rev, outcome_rev) plus the
%                 pattern-expression table and the Table 1 summary.
%                 Returned (not just saved) so the calling script can
%                 run cross-model comparisons (e.g. McNemar's test)
%                 without re-loading everything from disk.
%
%   Dependencies: CANlab Core Tools (fmri_data, canlab_pattern_similarity,
%                 roc_plot)

if ~exist(output_dir, 'dir'); mkdir(output_dir); end

%% User-defined paths (TO EDIT, if necessary)
datadir = fullfile(basedir, 'data');
sigdir  = fullfile(basedir, 'results', 'VITCS_development');   % where 02_train_VITCS_signature.m wrote its outputs
if ~exist(savedir, 'dir'); mkdir(savedir); end
maskdir = fullfile(datadir, 'brainmask.nii');

list_subj = {}; % <-- EDIT THIS, same as s01_train_test_split.m: list of subjects to include

contrastdir = '<PATHS_TO_CONTRAST_DATA>'; % <-- EDIT THIS: general path where all contrast data is stored
contrast_subpath = fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL'); % <-- EDIT IF YOUR FOLDER STRUCTURE DIFFERS

contrast_files = {{'<name_CS+_file>'; '<name_CS-_file>'}, ...
    {'<name_newCS+_file>'; '<name_newCS-_file>'}};
contrast_names = {{'CS+', 'CS-'}, {'newCS+', 'newCS-'}};
% 'CS+'/'CS-'       -> acquisition (Conditioning) contrasts
% 'newCS+'/'newCS-' -> reversal contrasts

metric = 'dot_product';

contrastdir = '/Users/acalvet/Documents/MVPA_FISAX/DATA/contrasts_brainmask';

contrast_files = {{'con_0011_mask'; 'con_0012_mask'}, ...
    {'con_0017_mask'; 'con_0018_mask'}};  % <-- EDIT THIS

contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}))';

%% Load signature and test set subject list
sig = fmri_data(sig_path, maskdir);

ts_set = load(fullfile(datadir, 'test_data.mat')).ts_set;
subj_ts = list_subj(ts_set);

%% Calculate and save pattern expression
res_pat_exp = array2table(zeros(length(subj_ts), 4), 'VariableNames', reshape([contrast_names{:}]', [], 1));
res_pat_exp.Properties.RowNames = subj_ts;

for C = 1:length(contrast_files)
    contrast_file = contrast_files{C};
    contrast_name = contrast_names{C};
    for i = 1:length(contrast_file)
        path_img = fullfile(contrastdir, subj_ts, contrast_subpath, [contrast_file{i} '.nii']);
        data_obj = fmri_data(path_img, maskdir);
        res_pat_exp{:, contrast_name{i}} = canlab_pattern_similarity(data_obj.dat, sig.dat, metric);
    end
end

writetable(res_pat_exp, fullfile(output_dir, sprintf('pat_exp_test_set_%s.xlsx', model_label)), 'WriteRowNames', true);

%% Classification performance (Table 1)
% Training set (10-fold CV) performance, for comparison alongside the
% test-set numbers. Produced by 02_train_VITCS_signature.m.
CV_roc_inputs = load(roc_inputs_path);

set_names = {'Training set (10-fold CV)', 'Test set - Acquisition', 'Test set - Reversal'};
res_table = array2table(zeros(3, 11), 'VariableNames', {'accuracy', 'acc_se', 'acc_p', ...
    'sensitivity', 'sensitivity_ci_I', 'sensitivity_ci_S', 'specificity', ...
    'specificity_ci_I', 'specificity_ci_S', 'AUC', 'cohens_d'});
res_table.Properties.RowNames = set_names;

% -- Training set (CV) --
dif_xval_dist = CV_roc_inputs.xval_dist_C1(CV_roc_inputs.outcome_C1 ...
    ) - CV_roc_inputs.xval_dist_C1(~CV_roc_inputs.outcome_C1) ;
d_cv = mean(dif_xval_dist)/std(dif_xval_dist); % Cohen's D

rp = roc_plot(CV_roc_inputs.xval_dist_C1, CV_roc_inputs.outcome_C1, 'threshold', 'pairedobservations');
res_table{set_names{1}, :} = [rp.accuracy, rp.accuracy_se, rp.accuracy_p, rp.sensitivity, ...
    rp.sensitivity_ci, rp.specificity, rp.specificity_ci, rp.AUC, d_cv];

% -- Test set: Acquisition (CS+/CS-) --
cont_acq = contrast_names{1};
dif_pat_exp_acq = res_pat_exp{:, cont_acq{1}} - res_pat_exp{:, cont_acq{2}};
d_acq = mean(dif_pat_exp_acq)/std(dif_pat_exp_acq); % Cohen's D

pat_exp_acq = [res_pat_exp{:, cont_acq{1}}; res_pat_exp{:, cont_acq{2}}];
outcome_acq = [ones(height(res_pat_exp), 1); zeros(height(res_pat_exp), 1)];
rp = roc_plot(pat_exp_acq, outcome_acq, 'threshold', 'pairedobservations');
res_table{set_names{2}, :} = [rp.accuracy, rp.accuracy_se, rp.accuracy_p, rp.sensitivity, ...
    rp.sensitivity_ci, rp.specificity, rp.specificity_ci, rp.AUC, d_acq];

% -- Test set: Reversal (newCS+/newCS-) --
cont_rev = contrast_names{2};
dif_pat_exp_rev = res_pat_exp{:, cont_rev{1}} - res_pat_exp{:, cont_rev{2}};
d_rev = mean(dif_pat_exp_rev)/std(dif_pat_exp_rev); % Cohen's D

pat_exp_rev = [res_pat_exp{:, cont_rev{1}}; res_pat_exp{:, cont_rev{2}}];
outcome_rev = [ones(height(res_pat_exp), 1); zeros(height(res_pat_exp), 1)];
rp = roc_plot(pat_exp_rev, outcome_rev, 'threshold', 'pairedobservations');
res_table{set_names{3}, :} = [rp.accuracy, rp.accuracy_se, rp.accuracy_p, rp.sensitivity, ...
    rp.sensitivity_ci, rp.specificity, rp.specificity_ci, rp.AUC, d_rev];

writetable(res_table, fullfile(output_dir, sprintf('table_test_set_values_%s.csv', model_label)), 'WriteRowNames', true);
fprintf('--- %s ---\n', model_label);
disp(res_table);

%% Save everything the fig02 b and c scripts need
results = struct();
results.model_label = model_label;
results.res_pat_exp = res_pat_exp;
results.res_table = res_table;
results.contrast_names = contrast_names;
results.subj_ts = subj_ts;
results.pat_exp_acq = pat_exp_acq;
results.outcome_acq = outcome_acq;
results.pat_exp_rev = pat_exp_rev;
results.outcome_rev = outcome_rev;
results.CV_roc_inputs = CV_roc_inputs;

save(fullfile(savedir, 'validation_test_set_results.mat'), '-struct', 'results');

end