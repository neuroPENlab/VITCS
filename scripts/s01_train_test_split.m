%% s01_train_test_split.m
% -------------------------------------------------------------------
% Split the full sample into a Training Set (80%) and an independent
% Test Set (20%), stratified by trait anxiety (STAI-T).
%
% From Methods: "The total dataset was split into a Training Set (80%
% of the sample; n = 138) for model development and an independent
% Test Set (20%; n = 34) for validation, stratified by STAI-T scores."
%
% Dependencies: MATLAB Statistics and Machine Learning Toolbox
%               (cvpartition, discretize)
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS
contrastdir = '<PATH_TO_CONTRASTS>';   % <-- EDIT THIS
datadir = fullfile(basedir, 'data');   % <-- if necessary, EDIT THIS
data_excel_path = '<PATH_TO_STAI-T_DATA>';   % <-- EDIT THIS
stai_t_var_name = 'STAI_T_A';   % <-- EDIT THIS: name of the column with STAI-T data

% O SI QUIEREN CAMBIAR LA FORMA...
contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));

% If true, load the exact Training/Test indices used in the manuscript
% (provided in this repository) instead of regenerating a new random
% split. Set to false only if you want to draw a fresh stratified split
% from scratch (this will NOT reproduce the published partition, since
% the original random seed was not recorded).
USE_PUBLISHED_SPLIT = true;

%% Load questionnaire data 
data_excel = readtable(data_excel_path, 'VariableNamingRule', 'preserve');
subj_names = data_excel.subject_id; % List of subject with clinical data
data_excel.Properties.RowNames = subj_names;
data_excel.subject_id = [];

% Keep only subjects with usable neuroimaging data
valid_subjects = ismember(subj_names, list_subj);
data_excel = data_excel(valid_subjects, :);

%% Train/test split 
if USE_PUBLISHED_SPLIT

    tr_set = load(fullfile(datadir, 'training_data.mat')).tr_set;
    ts_set = load(fullfile(datadir, 'test_data.mat')).ts_set;

else
    % Stratify on STAI-T quintiles so that both sets have comparable
    % trait-anxiety.
    edges = quantile(data_excel.(stai_t_var_name), 5);
    strat_group = discretize(data_excel.(stai_t_var_name), [-inf, edges, inf]);

    C = cvpartition(strat_group, 'HoldOut', 0.2, 'Stratify', true);
    tr_set = training(C);
    ts_set = test(C);

    save(fullfile(datadir, 'training_data.mat'), 'tr_set');
    save(fullfile(datadir, 'test_data.mat'), 'ts_set');

end

fprintf('Training set: n = %d\n', sum(tr_set));
fprintf('Test set:     n = %d\n', sum(ts_set));