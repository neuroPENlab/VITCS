function results = run_test_set_validation(basedir, contrastdir, contrast_subpath, ...
    contrast_files, contrast_names, sig_path, output_dir, model_label, perm_test, nperm)
%   Evaluate a VITCS-family signature on the Test Set.
%
%   results = RUN_TEST_SET_VALIDATION(basedir, contrastdir, contrast_subpath, ...
%   contrast_files, contrast_names, sig_path, output_dir, model_label, perm_test, nperm)
%
%   INPUTS
%       basedir          - project root
%       contrastdir      - directory containing one subfolder per subject with 
%                          that subject's first-level contrast images
%       contrast_subpath - subfolder path (relative to each subject's folder in 
%                          contrastdir) where the contrast images live, e.g.
%                          fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL')
%       contrast_files   - cell array of contrast image filenames (without extension) 
%                          to compute pattern expression for, e.g. {'con001'; 'con002'}
%       contrast_names   - cell array of column names (same length/order as 
%                          contrast_files), e.g. {'CS+', 'CS-'}
%       sig_path         - path to this model's unthresholded signature .nii 
%                          (from run_signature_training.m)
%       output_dir       - directory to write this model's evaluation outputs to
%       model_label      - short string used in filenames, e.g. 'VITCS_acq', 
%                          'VITCS_rev', 'VITCS_early', 'VITCS_late' ...
%      (Optional)
%       perm_test        - perform permutation test (default false)
%       nperm            - number of permutations (default 10000)
%
%   OUTPUT
%       results - struct with per-participant distances/outcomes for the 
%                 specific contrasts plus the pattern-expression values.
%                 Also number of permutations and p-value if perm_test
%                 true.
%
%   Dependencies: CANlab Core Tools (fmri_data, canlab_pattern_similarity,
%                 roc_plot)

if nargin < 9 || isempty(perm_test)
    perm_test = false;
end

if nargin < 10 || isempty(nperm)
    nperm = 10000;
end

if ~exist(output_dir, 'dir'); mkdir(output_dir); end

%% User-defined paths (TO EDIT, if necessary)
datadir = fullfile(basedir, 'data');
maskdir = fullfile(datadir, 'brainmask.nii');

metric = 'dot_product';

contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));

%% Load signature and test set subject list
sig = fmri_data(sig_path, maskdir);

ts_set = load(fullfile(datadir, 'test_data.mat')).ts_set;
subj_ts = list_subj(ts_set);

%% Calculate and save pattern expression
res_pat_exp = array2table(zeros(length(subj_ts), numel(contrast_names)), ...
    'VariableNames', contrast_names);
res_pat_exp.Properties.RowNames = subj_ts;

for C = 1:length(contrast_files)
    contrast_file = contrast_files{C};
    contrast_name = contrast_names{C};
    path_img = fullfile(contrastdir, subj_ts, contrast_subpath, [contrast_file '.nii']);
    data_obj = fmri_data(path_img, maskdir);
    res_pat_exp{:, contrast_name} = canlab_pattern_similarity(data_obj.dat, sig.dat, metric);
end

writetable(res_pat_exp, fullfile(output_dir, [model_label 'pat_exp_test_set.xlsx']), 'WriteRowNames', true);

%% Classification performance
res_table = array2table(zeros(1, 13), 'VariableNames', {'accuracy', 'acc_se', 'acc_p', ...
    'sensitivity', 'sensitivity_ci_I', 'sensitivity_ci_S', 'specificity', ...
    'specificity_ci_I', 'specificity_ci_S', 'AUC', 'AUC_ci_I', 'AUC_ci_S', 'cohens_d'});
res_table.Properties.RowNames = {model_label};

dif_pat_exp = res_pat_exp{:, contrast_names{1}} - res_pat_exp{:, contrast_names{2}};
d = mean(dif_pat_exp)/std(dif_pat_exp); % Cohen's D

pat_exp = [res_pat_exp{:, contrast_names{1}}; res_pat_exp{:, contrast_names{2}}];
outcome = [ones(height(res_pat_exp), 1); zeros(height(res_pat_exp), 1)];
rp = roc_plot(pat_exp, outcome, 'threshold', 'pairedobservations');
auc_ci = bootstrap_auc_ci(res_pat_exp{:, contrast_names{1}}, res_pat_exp{:, contrast_names{2}}, 5000, 1);
res_table{model_label, :} = [rp.accuracy, rp.accuracy_se, rp.accuracy_p, rp.sensitivity, ...
    rp.sensitivity_ci, rp.specificity, rp.specificity_ci, rp.AUC, auc_ci, d];

writetable(res_table, fullfile(output_dir, [model_label '_test_set_values.csv']), 'WriteRowNames', true);
fprintf('--- %s ---\n', model_label);
disp(res_table);

%% Save everything the fig02 b and c scripts need
results = struct();
results.model_label = model_label;
results.res_pat_exp = res_pat_exp;
results.res_table = res_table;
results.contrast_names = contrast_names;
results.subj_ts = subj_ts;
results.pat_exp = pat_exp;
results.outcome = outcome;

save(fullfile(output_dir, [model_label '_validation_test_set_results.mat']), '-struct', 'results');

if perm_test
    seed  = 20261019;      % fixed seed -> reproducible permutations
    
    % Subjects and Training/Test split
    tr_set = load(fullfile(datadir, 'training_data.mat')).tr_set;
    subj_tr = list_subj(tr_set);
    subj_ts = list_subj(ts_set);
    n_tr = numel(subj_tr);
    
    getpaths = @(subj, name) fullfile(contrastdir, subj, contrast_subpath, [name '.nii']);
    
    % Load data
    % Training: columns = [CS+ of all training subjects, CS- of the same subjects]
    training_data = fmri_data([getpaths(subj_tr, contrast_files{1}), getpaths(subj_tr, contrast_files{2})], maskdir);
    training_data.Y = [ones(n_tr, 1); -ones(n_tr, 1)];
    
    % Test set (voxels x participants)
    X_p = fmri_data(getpaths(subj_ts, contrast_files{1}), maskdir).dat;
    X_m = fmri_data(getpaths(subj_ts, contrast_files{2}), maskdir).dat;

    % Forced-choice accuracy of a weight map w (voxels x 1) on a set of pairs
    fc_acc = @(w, Xp, Xm) mean((w' * Xp) > (w' * Xm));
    
    % Observed accuracy (the real, saved VITCS model)
    w_obs = sig.dat;
    acc_obs = fc_acc(w_obs, X_p, X_m);
    
    % Sanity check: re-training with the REAL labels must reproduce the saved model
    svm_args = {'algorithm_name', 'cv_svm', 'nfolds', 1, 'C', 1, 'error_type', 'mcr', ...
        'useparallel', 0, 'verbose', 0};   % nfolds = 1 -> fit on all training data, no CV
    [~, st0] = predict(training_data, svm_args{:});
    w0 = st0.weight_obj.dat;
    fprintf('Cosine similarity, re-trained (real labels) vs saved VITCS: %.4f (should be ~1)\n', ...
        (w0' * w_obs) / (norm(w0) * norm(w_obs)));
    
    % Permutations (random label swap within each training participant)
    rng(seed);
    signs = randi(2, n_tr, nperm) * 2 - 3;   % +1 = keep labels, -1 = swap CS+/CS- (per participant)
    
    null = nan(nperm, 1);
    for ip = 1:nperm
        d = training_data;
        d.Y = [signs(:, ip); -signs(:, ip)];       % CS+ image gets s, CS- image gets -s
        [~, st] = predict(d, svm_args{:});
        w = st.weight_obj.dat;
        null(ip) = fc_acc(w, X_p, X_m);  % tested against INTACT labels
    end
    
    % p-values (one-sided: null accuracy >= observed accuracy)
    tol = 1e-12;
    p = (sum(null >= acc_obs - tol) + 1) / (nperm + 1);
    
    fprintf('\nObserved %.3f | null mean %.3f (SD %.3f, max %.3f) | p = %.4f\n', ...
        acc_obs, mean(null), std(null), max(null), p);
    
    % Save
    res = table(acc_obs, mean(null), std(null), max(null), p, nperm, ...
        'VariableNames', {'observed_accuracy', 'null_mean', 'null_sd', 'null_max', 'p_perm', 'nperm'});
    res.Properties.RowNames = {model_label};
    writetable(res, fullfile(output_dir, [model_label '_permutation_test_test_set.csv']));

    results.nperm = nperm;
    results.pperm = p;
end

end