%% s04_generalization_ENIGMA.m
% -------------------------------------------------------------------
% Compute pattern expression of VITCS (and its early/late variants)
% and two comparison signatures (Reddan-Threat, Liu-SUITAS) across the
% 26 harmonized threat-conditioning datasets from the ENIGMA-Anxiety
% Fear Conditioning Group (N = 1,898; see Table 2).
%
% From Methods: "Model generalizability was evaluated using 26
% independent datasets from the ENIGMA-Anxiety FC Group. [...]
% Individual participant-level contrast images (CS+ > CS-) were shared
% with the central analysis team, and VITCS expression values were
% computed centrally as the dot product between each contrast image
% and the VITCS weight map."
%
% This script only computes pattern expression per participant/
% signature and writes a results table; dataset-level filtering,
% accuracy by US modality, and comparison-signature statistics are
% computed downstream in 04_analysis_ENIGMA.py (kept in Python since
% the ENIGMA collaborators' original analysis pipeline was in Python).
%
% Dependencies: CANlab Core Tools (fmri_data, resample_space,
%               canlab_pattern_similarity, load_image_set)
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
basedir = '/Users/acalvet/Repositories/neuroPENlab/VITCS';
datadir = fullfile(basedir, 'data');   % <-- if necessary, EDIT THIS
savedir = fullfile(basedir, 'results', 'VITCS_ENIGMA_generalization');   % <-- if necessary, EDIT THIS
if ~exist(savedir, 'dir'); mkdir(savedir); end

maskdir = fullfile(datadir, 'brainmask.nii');
metric = 'dot_product';

%% Participant-level data
% This table (contrast image path, dataset ID, age, sex, group,
% diagnosis, US type, etc. per ENIGMA-Anxiety FC participant) is
% restricted, multi-site consortium data and is not published. 
excel_path = '<PATH_TO_ENIGMA_PARTICIPANT_TABLE>'; % <-- EDIT THIS
excel = readtable(excel_path, 'VariableNamingRule', 'preserve');
excel.Properties.RowNames = cellstr(num2str(excel.Var1));

%% Load brain signatures
% Each entry: {display name, fmri_data object}. Adding a new signature
% to compare against ENIGMA data only requires adding a row here - the
% pattern expression loop below is identical for all of them.
signatures = {
    'VITCS',       fmri_data(fullfile(basedir, 'results', 'VITCS_development', 'VITCS_unthresholded_10foldCV.nii'), maskdir)
    'VITCS_early', fmri_data(fullfile(basedir, 'results', 'VITCS_development_early', 'VITCS_unthresholded_10foldCV.nii'), maskdir)
    'VITCS_late',  fmri_data(fullfile(basedir, 'results', 'VITCS_development_late',  'VITCS_unthresholded_10foldCV.nii'), maskdir)
    'Reddan_Threat', load_image_set('csplus')
    'Liu_SUITAS',  fmri_data('<PATH_TO_SUITAS_SIGNATURE>', maskdir) % <-- EDIT THIS
};

%% Calculate pattern expression for all signatures
data_obj = fmri_data(excel.path, maskdir);

pat_exp = zeros(height(excel), size(signatures, 1));
for s = 1:size(signatures,1)
    sig_resampled = resample_space(signatures{s, 2}, data_obj);
    pat_exp(:, s) = canlab_pattern_similarity(data_obj.dat, sig_resampled.dat, metric);
end

%% Save results
res_pat_exp = array2table(pat_exp, 'VariableNames', signatures(:, 1));
res_pat_exp.Properties.RowNames = cellstr(num2str(excel.Var1));

excel_pat = join(excel, res_pat_exp, 'Keys', 'Row');
writetable(excel_pat, fullfile(savedir, 'pattern_expression_ENIGMA_all_signatures.xlsx'));