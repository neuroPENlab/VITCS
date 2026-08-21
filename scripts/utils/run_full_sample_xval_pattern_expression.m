function run_full_sample_pattern_expression(basedir, contrast_files, contrast_names, sigdir, output_dir)
% canviar CSp_file, CSm_file per list dels noms dels contrasts?

%   Pattern expression (CS+/CS-) for the full sample (training + test subjects).
%
%   RUN_FULL_SAMPLE_PATTERN_EXPRESSION(basedir, CSp_file, ...
%       CSm_file, sigdir, output_dir)
%
%   For each training-set subject, pattern expression is computed using
%   the weight map from the 10-fold CV fold that LEFT THAT SUBJECT OUT
%   (out-of-fold prediction), so no subject's value comes from a model
%   trained on them. Test-set subjects use the full trained model
%   directly.
%
%   INPUTS
%       basedir     - project root
%       CSp_file    - contrast filename for CS+ (e.g. 'con_0011_mask')
%       CSm_file    - contrast filename for CS- (e.g. 'con_0012_mask')
%       sigdir      - directory with this model's VITCS_unthresholded_10foldCV.nii
%                     and VITCS_cv_fold_weights.mat (from run_VITCS_training.m)
%       output_dir  - directory to write pat_exp_full_sample_xval.xlsx to
%
%   Dependencies: CANlab Core Tools (fmri_data, canlab_pattern_similarity)

%% Paths
datadir = fullfile(basedir, 'data');
maskdir = fullfile(datadir, 'brainmask.nii');

contrastdir = '<PATHS_TO_CONTRAST_DATA>'; % <-- EDIT THIS: same as elsewhere
contrast_subpath = fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL'); % <-- EDIT IF YOUR FOLDER STRUCTURE DIFFERS

metric = 'dot_product';

% COM HO FEM AIXO???
list_subj = {}; % <-- EDIT THIS, same as s01_train_test_split.m: list of subjects to include

% contrastdir = '<PATHS_TO_CONTRAST_DATA>'; % <-- EDIT THIS: general path where all contrast data is stored
% contrast_subpath = fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL'); % <-- EDIT IF YOUR FOLDER STRUCTURE DIFFERS

contrastdir = '/Users/acalvet/Documents/MVPA_FISAX/DATA/contrasts_brainmask';
contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));

%% Load subject data, train/test split, and per-fold model weights 
tr_set = load(fullfile(datadir, 'training_data.mat')).tr_set;

cv_weights = load(fullfile(sigdir, 'VITCS_cv_10fold_weights.mat')); % other_output_cv, sample_folds
sig = fmri_data(fullfile(sigdir, 'VITCS_unthresholded_10foldCV.nii'), maskdir);

%% Compute out-of-fold (training) / full-model (test) pattern expression
res_pat_exp = array2table(nan(length(list_subj), length(contrast_files)), 'VariableNames', all_names);
res_pat_exp.Properties.RowNames = list_subj;

fold_counter = 1;   % index into sample_folds/other_output_cv, increments only for training subjects
for s = 1:length(list_subj)
    subj = list_subj{s};

    if tr_set(s) == 1 % Training data
        this_fold = cv_weights.sample_folds(fold_counter, 1);
        sig_xval = fmri_data(maskdir);
        sig_xval.dat = cv_weights.other_output_cv{this_fold, 1};
        fold_counter = fold_counter + 1;
    else % Test data
        sig_xval = sig;
    end
    % Pattern expression per each contrast file
    for c = 1:length(contrast_files)
        path_img = fullfile(contrastdir, subj, contrast_subpath, [contrast_files{c} '.nii']);
        data_obj = fmri_data(path_img, maskdir);
        res_pat_exp{subj, contrast_names{c}{i}} = canlab_pattern_similarity(data_obj.dat, sig_xval.dat, metric);
    end
end

%% Save results
writetable(res_pat_exp, fullfile(output_dir, 'pat_exp_full_sample_xval.xlsx'), 'WriteRowNames', true);

end