%% s04_1_generalization_ENIGMA.m
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
% Run once per signature: set SIGNATURE below and re-run.
%
% Dependencies: CANlab Core Tools (fmri_data, resample_space,
%               canlab_pattern_similarity, load_image_set)
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
datadir = fullfile(basedir, 'data');   % <-- if necessary, EDIT THIS

maskdir = fullfile(datadir, 'brainmask.nii');
metric = 'dot_product';

%% Participant-level data
% This table (contrast image path, dataset ID, age, sex, group,
% diagnosis, US type, etc. per ENIGMA-Anxiety FC participant) is
% restricted, multi-site consortium data and is not published. 
excel_path = '<PATH_TO_ENIGMA_PARTICIPANT_TABLE>'; % <-- EDIT THIS
excel = readtable(excel_path, 'VariableNamingRule', 'preserve');
excel.Properties.RowNames = cellstr(num2str(excel.Var1));

%% Which signature to run mediation for
SIGNATURE = 'VITCS'; % <-- EDIT THIS: 'VITCS' | 'Reddan-Threat' | 'Liu-SUITAS' | 'VITCS_early' | 'VITCS_late'

switch SIGNATURE
    case 'VITCS'
        sig = fmri_data(fullfile(basedir, 'results', 'VITCS_development', ...
            'VITCS_unthresholded_10foldCV.nii'), maskdir);
        savedir = fullfile(basedir, 'results', 'VITCS_ENIGMA_generalization');
    case 'Reddan-Threat'
        sig = load_image_set('csplus');
        savedir = fullfile(basedir, 'results', 'comparison_existing_signatures');
    case 'Liu-SUITAS'
        sig = fmri_data('<PATH_TO_SUITAS_SIGNATURE>', maskdir); % <-- EDIT THIS
        savedir = fullfile(basedir, 'results', 'comparison_existing_signatures');
    case 'VITCS_early'
        sig = fmri_data(fullfile(basedir, 'results', 'VITCS_early_results', ...
            'VITCS_unthresholded_10foldCV.nii'), maskdir);
        savedir = fullfile(basedir, 'results', 'VITCS_early_results');
    case 'VITCS_late'
        sig = fmri_data(fullfile(basedir, 'results', 'VITCS_late_results',  ...
            'VITCS_unthresholded_10foldCV.nii'), maskdir);
        savedir = fullfile(basedir, 'results', 'VITCS_late_results');
end

if ~exist(savedir, 'dir'); mkdir(savedir); end

%% Calculate pattern expression for all signatures
data_obj = fmri_data(excel.path, maskdir);
sig_resampled = resample_space(sig, data_obj);
pat_exp = canlab_pattern_similarity(data_obj.dat, sig_resampled.dat, metric);

%% Save results
res_pat_exp = array2table(pat_exp, 'VariableNames', {SIGNATURE});
res_pat_exp.Properties.RowNames = cellstr(num2str(excel.Var1));

excel_pat = join(excel, res_pat_exp, 'Keys', 'Row');
writetable(excel_pat, fullfile(savedir, ['pattern_expression_ENIGMA_' SIGNATURE '.xlsx']));
