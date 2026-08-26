%% s09_comparison_existing_signatures.m
% -------------------------------------------------------------------
% Benchmark VITCS against previously published affective/threat-related
% brain signatures: pattern expression, classification accuracy, 
% pairwise significance comparisons, and shared variance with VITCS.
%
% From Results: "the VITCS significantly outperformed all existing
% signatures, even under conservative correction for multiple
% comparisons (McNemar Pairwise, p<0.01; Fig. 4). Differences among
% several previously published threat-, fear- and pain-related brain
% signatures were not statistically significant (Supplementary Table
% 5)." And: "we quantified the proportion of shared variance (R^2)
% between VITCS pattern expression and the outputs of each benchmark
% signature during CS+ trials across participants [...] (Table 5)."
%
% To RUN NEXT STEPS (ENIGMA, mediation and anxiety risk analyses):
%   (1) s04_1_generalization_ENIGMA.m and s04_2_generalization_ENIGMA_analysis.py
%       with SIGNATURE = 'Reddan-Threat' and = 'Liu-SUITAS'
%   (2) s07_mediation_analysis.m with SIGNATURE = 'Reddan-Threat' and = 'Liu-SUITAS'
%   (3) s08_anxiety_risk_analysis.py with SIGNATURE = 'Reddan-Threat' and = 'Liu-SUITAS'
%
% Dependencies: CANlab Core Tools (fmri_data, canlab_pattern_similarity,
%               load_image_set, roc_plot, correlation),
%               Statistics and Machine Learning Toolbox (binocdf, mafdr)
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
contrastdir = '<PATH_TO_CONTRASTS>';   % <-- EDIT THIS
contrast_subpath = fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL'); % <-- EDIT IF YOUR FOLDER STRUCTURE DIFFERS

datadir = fullfile(basedir, 'data');
vitcs_dir = fullfile(basedir, 'results', 'VITCS_development');  % where pat_exp_full_sample_xval.xlsx
maskdir = fullfile(datadir, 'brainmask.nii');
savedir = fullfile(basedir, 'results', 'comparison_existing_signatures');   % <-- if necessary, EDIT THIS
if ~exist(savedir, 'dir'); mkdir(savedir); end

contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));

contrast_files = {'<name_CS+_file>'; '<name_CS-_file>'};     % <-- EDIT THIS
contrast_names = {'CS+', 'CS-'};

metric = 'dot_product';

%% Load brain signatures
% Each entry: {display name, fmri_data object, column index within that 
% object to use}. Adding a new signature to compare against ENIGMA data 
% only requires adding a row here.
liu_suitas_path = '<PATH_TO_LIU_SUITAS_SIGNATURE>';       % <-- EDIT THIS
wen_beyondthreat_path = '<PATH_TO_WEN_BEYONDTHREAT_SIGNATURE>';    % <-- EDIT THIS
wager_nps_path = '<PATH_TO_WAGER_NPS_SIGNATURE>';           % <-- EDIT THIS

multiaversive = load_image_set('multiaversive');
signatures = {
    'Reddan-Threat', load_image_set('csplus'), 1
    'Liu-SUITAS', load_image_set({liu_suitas_path}), 1
    'Zhou-VIFS', fmri_data(which('VIFS.nii')), 1
    'Wen-BeyondThreat', load_image_set({wen_beyondthreat_path}), 1
    'Wager-NPS', load_image_set({wager_nps_path}), 1
    'Ceko-Common_NA', multiaversive, 1
    'Ceko-Mechanical_NA', multiaversive, 2
    'Ceko-Thermal_NA', multiaversive, 3
    'Ceko-Sound_NA', multiaversive, 4
    'Ceko-Visual_NA', multiaversive, 5
    'Koban-NCS', load_image_set('ncs'), 1
};

%% Compute CS+/CS- pattern expression for each comparison signature
col_names = {};
for i = 1:size(signatures, 1)
    for j = 1:numel(contrast_names)
        col_names{end+1} = sprintf('%s_%s', signatures{i,1}, contrast_names{j});
    end
end

res_pat_exp = array2table(zeros(length(list_subj), length(col_names)), 'VariableNames', col_names);
res_pat_exp.Properties.RowNames = list_subj;

for c = 1:length(contrast_names)
    data_obj = fmri_data(fullfile(contrastdir, list_subj, contrast_subpath, [contrast_files{c} '.nii']), maskdir);
    for s = 1:size(signatures,1)
        if ~(startsWith(signatures{s,1}, 'Ceko-') && ~contains(signatures{s, 1}, 'Common'))
            sig_resampled = resample_space(signatures{s, 2}, data_obj);
        end
        res_pat_exp{:, [signatures{s,1} '_' contrast_names{c}]} = canlab_pattern_similarity(data_obj.dat, ...
            sig_resampled.dat(:, signatures{s, 3}), metric);
    end
end

%% Merge with VITCS's already-computed full-sample pattern expression
vitcs_pat_exp = readtable(fullfile(vitcs_dir, 'pat_exp_full_sample_xval.xlsx'), 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
vitcs_pat_exp.Properties.VariableNames = {'VITCS_CS+', 'VITCS_CS-'};

res_pat_exp = [vitcs_pat_exp, res_pat_exp];
writetable(res_pat_exp, fullfile(savedir, 'pat_exp_full_sample_all_signatures.xlsx'), 'WriteRowNames', true);

%% Accuracy per signature (forced-choice CS+ vs CS-)
sig_names = [{'VITCS'}, signatures(:, 1)'];
res_accuracy = array2table(zeros(length(sig_names), 6), 'VariableNames', {'acc', 'acc_p', 'acc_se', 'sens', 'spec','auc'});
res_accuracy.Properties.RowNames = sig_names;

res_forced_choice = array2table(zeros(length(list_subj), length(sig_names)), 'VariableNames', sig_names);
res_forced_choice.Properties.RowNames = list_subj;

for i = 1:length(sig_names)
    csp = res_pat_exp.([sig_names{i} '_CS+']);
    csm = res_pat_exp.([sig_names{i} '_CS-']);

    res_forced_choice{:, sig_names{i}} = csp > csm;

    rp = roc_plot([csp; csm], [ones(length(csp), 1); zeros(length(csm), 1)], 'threshold', 'pairedobservations');
    res_accuracy{sig_names{i}, :} = [rp.accuracy, rp.accuracy_p, rp.accuracy_se, rp.sensitivity, rp.specificity, rp.AUC];
end

writetable(res_accuracy, fullfile(savedir, 'accuracy_all_signatures.csv'), 'WriteRowNames', true);
disp(res_accuracy);

%% Pairwise significance comparisons (Supplementary Table 5)
% Exact binomial test on discordant forced-choice outcomes between each
% pair of signatures (same statistic as McNemar's exact test).
n_sig = length(sig_names);
p_mat = nan(n_sig, n_sig);
n01_mat = nan(n_sig, n_sig);
n10_mat = nan(n_sig, n_sig);

for i = 1:n_sig
    for j = i+1:n_sig
        n01 = sum(~res_forced_choice{:, i} & res_forced_choice{:, j});  % i wrong, j right
        n10 = sum(res_forced_choice{:, i} & ~res_forced_choice{:, j});  % i right, j wrong
        p = min(1, binocdf(min(n01, n10), n01 + n10, 0.5) * 2);

        p_mat(i, j) = p;
        n01_mat(j, i) = n01;
        n10_mat(j, i) = n10;
    end
end

dif_p_signatures_all = array2table(p_mat, 'VariableNames', sig_names, 'RowNames', sig_names);
dif_n01_signatures_all = array2table(n01_mat, 'VariableNames', sig_names, 'RowNames', sig_names);
dif_n10_signatures_all = array2table(n10_mat, 'VariableNames', sig_names, 'RowNames', sig_names);

% Correct by multiple comparisons
mask = triu(true(n_sig), 1);
p_fdr = mafdr(p_mat(mask), 'BHFDR', true); % FDR (Benjamini-Hochberg)

% Matrix reconstruction
p_mat_fdr = nan(n_sig);
p_mat_fdr(mask) = p_fdr;
dif_p_signatures_all_corr = array2table(p_mat_fdr, 'VariableNames', sig_names, 'RowNames', sig_names);

writetable(dif_p_signatures_all, fullfile(savedir, 'pairwise_p_uncorrected.csv'), 'WriteRowNames', true);
writetable(dif_p_signatures_all_corr, fullfile(savedir, 'pairwise_p_fdr_corrected.csv'), 'WriteRowNames', true);
writetable(dif_n01_signatures_all, fullfile(savedir, 'pairwise_n01_McNemar.xlsx'), 'WriteRowNames', true);
writetable(dif_n10_signatures_all, fullfile(savedir, 'pairwise_n10_McNemar.xlsx'), 'WriteRowNames', true);

%% Shared variance (R^2) between VITCS and each comparison signature, CS+ only
r_res = array2table(zeros(length(sig_names), 1), 'VariableNames', {'CS+_r'}, 'RowNames', sig_names);
p_res = array2table(zeros(length(sig_names), 1), 'VariableNames', {'CS+_p'}, 'RowNames', sig_names);

for i = 1:length(sig_names)
    [r_res{sig_names{i}, 'CS+_r'}, ~, p_res{sig_names{i}, 'CS+_p'}] = correlation('r', ...
        res_pat_exp.("VITCS_CS+"), res_pat_exp.(sig_names{i} + "_CS+"));
end

r2_res = array2table(r_res.('CS+_r') .^ 2, 'VariableNames', {'R2'}, 'RowNames', sig_names);
q_res = array2table(mafdr(p_res.('CS+_p'), 'BHFDR', true), 'VariableNames', {'q_fdr'}, 'RowNames', sig_names);

shared_variance_table = [r_res, r2_res, p_res, q_res];
writetable(shared_variance_table, fullfile(savedir, 'shared_variance_vs_VITCS.csv'), 'WriteRowNames', true);
disp(shared_variance_table);