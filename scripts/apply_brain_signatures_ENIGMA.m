clear; clc;
basedir = '/Users/acalvet/Documents/MVPA_FISAX';
save_results = fullfile(basedir,'TFM_git', 'results', 'final_brainmask', 'ENIGMA_FC', 'results');
maskdir = fullfile(basedir, 'DATA', 'brainmask_canlab_bin_resampled.nii');
% maskdir = fullfile(basedir, 'DATA', 'neurosynth_masks', 'neurosynth_mask_final', ...
%     'neurosynth_mask_open2_dil2_resampled_dmn_somamotor2.nii');

excel = readtable(fullfile(basedir,'TFM_git', 'results', 'final_brainmask', 'ENIGMA_FC', ...
    'path_info_subj_moreinfo.xlsx'),'VariableNamingRule','preserve');
excel.Properties.RowNames = cellstr(num2str(excel.Var1));

metric = 'dot_product';

%% Load brain signatures
vitcs = fmri_data(fullfile(basedir,'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai', 'svm_results_unthresholded.nii'), maskdir);
vitcs_early = fmri_data(fullfile(basedir,'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai_early', 'svm_results_unthresholded.nii'), maskdir);
vitcs_late = fmri_data(fullfile(basedir,'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai_late', 'svm_results_unthresholded.nii'), maskdir);
% Reddan - threat signature
threat2 = load_image_set('csplus');
% Liu - SUITAS
% [suitas, ] = load_image_set({fullfile(basedir,'TFM_git', 'results', 'final_brainmask', '1_sig_evaluation', 'signatures', '3_Liu_SUITAS_Induced20_z.nii')});

% signatures = {vitcs, threat, suitas}; %, threat, suitas
signatures = {vitcs, vitcs_early, vitcs_late}; %, threat, suitas
% sig_names = {'VITCS', 'reddan', 'suitas'}; %, 'Threat', 'SUITAS'
sig_names = {'VITCS', 'VITCS_early', 'VITCS_late'}; %, 'Threat', 'SUITAS'

sub_subj = excel;

%% Calculate pattern expression and save results
data_obj = fmri_data(sub_subj.path, maskdir);

% Calculate pattern expression
for s = 1:length(signatures)
    sig_resampled = resample_space(signatures{s}, data_obj);
    pat_exp(:, s) = canlab_pattern_similarity(data_obj.dat, sig_resampled.dat, metric);
end

% Table for pattern expression values
% Els contrasts són CS+ > CS-, per tant, el valor hauria de ser positiu
res_pat_exp = array2table(pat_exp, 'VariableNames', sig_names);
res_pat_exp.Properties.RowNames = cellstr(num2str(excel.Var1));
excel_pat = join(excel, res_pat_exp, 'Keys', 'Row');
writetable(excel_pat, fullfile(save_results, 'pattern_ENIGMA_vitcs_early_late.xlsx'));

%% Separem per tipus de dataset
% ROC_CV = roc_plot(double(pat_exp > 0), true(size(pat_exp)));
% Plotegem
colors = containers.Map({0, 1}, {[0 0 1], [1 0 0]}); % M=0, F=1
markers = containers.Map({'healthy', 'patient'}, {'o', 'square'});
unique_datasets = unique(excel_pat.dataset);

for d = 1:length(unique_datasets)
    d_name = unique_datasets{d};
    subset = excel_pat(strcmp(excel_pat.dataset, d_name), :);
    % subset = excel_pat;

    acc_all = sum(subset.VITS > 0)/height(subset) * 100; % acc =  sensitivity
    acc_controls = table2array(sum(subset(strcmp(subset.group, 'healthy'), 'VITS') > 0))/sum(strcmp(subset.group, 'healthy')) * 100;
    acc_patients = table2array(sum(subset(strcmp(subset.group, 'patient'), 'VITS') > 0))/sum(strcmp(subset.group, 'patient')) * 100;

    figure;
    hold on;
    for i = 1:height(subset)
        scatter(subset.age(i), subset.VITS(i), 60, 'MarkerFaceColor', colors(subset.sex(i)), ...
            'Marker', markers(subset.group{i}), 'MarkerEdgeColor', 'k');
    end
    h_legend(1) = scatter(nan, nan, 60, 'MarkerFaceColor', [0 0 1], 'Marker', 'o', 'MarkerEdgeColor', 'k');
    h_legend(2) = scatter(nan, nan, 60, 'MarkerFaceColor', [1 0 0], 'Marker', 'o', 'MarkerEdgeColor', 'k');
    h_legend(3) = scatter(nan, nan, 60, 'MarkerFaceColor', [0 0 1], 'Marker', 's', 'MarkerEdgeColor', 'k');
    h_legend(4) = scatter(nan, nan, 60, 'MarkerFaceColor', [1 0 0], 'Marker', 's', 'MarkerEdgeColor', 'k');
    xlabel('Age', 'FontSize', 16);
    ylabel('Patter expression (VITS)', 'FontSize', 16);
    title(['Dataset: ', replace(d_name, '_', ' '), ' by Sex and Group'], 'FontSize', 20);
    subtitle(['Acc (all) = ' num2str(acc_all) '; acc (healthy) = ' num2str(acc_controls) '; acc (patients) = ' num2str(acc_patients)], 'FontSize', 18);
    legend(h_legend, {'M, healthy', 'F, healthy', 'Male, patient', 'Female, patient'}, 'Location', 'best');
    ax = gca;
    ax.FontSize = 14;
    hold off;
end

dataset_prefixes = cellfun(@(x) regexp(x, '^[^_]+_[^_]+', 'match', 'once'), unique_datasets, 'UniformOutput', false);
unique_prefixes = unique(dataset_prefixes);
grouped_datasets = containers.Map();
for j = 1:length(unique_prefixes)
    prefix = unique_prefixes{j};
    matching_datasets = unique_datasets(strcmp(dataset_prefixes, prefix));
    grouped_datasets(prefix) = matching_datasets;

    subset_table = excel_pat(startsWith(excel_pat.dataset, prefix), :);

    acc_all = sum(subset_table.VITS > 0)/height(subset_table) * 100; % acc = sensitivity
    acc_controls = table2array(sum(subset_table(strcmp(subset_table.group, 'healthy'), 'VITS') > 0))/sum(strcmp(subset_table.group, 'healthy')) * 100;
    acc_patients = table2array(sum(subset_table(strcmp(subset_table.group, 'patient'), 'VITS') > 0))/sum(strcmp(subset_table.group, 'patient')) * 100;

    figure;
    hold on;
    for i = 1:height(subset_table)
        scatter(subset_table.age(i), subset_table.VITS(i), 60, 'MarkerFaceColor', colors(subset_table.sex(i)), ...
            'Marker', markers(subset_table.group{i}), 'MarkerEdgeColor', 'k');
    end
    h_legend(1) = scatter(nan, nan, 60, 'MarkerFaceColor', [0 0 1], 'Marker', 'o', 'MarkerEdgeColor', 'k');
    h_legend(2) = scatter(nan, nan, 60, 'MarkerFaceColor', [1 0 0], 'Marker', 'o', 'MarkerEdgeColor', 'k');
    h_legend(3) = scatter(nan, nan, 60, 'MarkerFaceColor', [0 0 1], 'Marker', 's', 'MarkerEdgeColor', 'k');
    h_legend(4) = scatter(nan, nan, 60, 'MarkerFaceColor', [1 0 0], 'Marker', 's', 'MarkerEdgeColor', 'k');
    xlabel('Age', 'FontSize', 16);
    ylabel('Patter expression (VITS)', 'FontSize', 16);
    title(['Dataset: ', replace(prefix, '_', ' '), ' by Sex and Group'], 'FontSize', 20);
    subtitle(['Acc (all) = ' num2str(acc_all) '; acc (healthy) = ' num2str(acc_controls) '; acc (patients) = ' num2str(acc_patients)], 'FontSize', 18);
    legend(h_legend, {'M, healthy', 'F, healthy', 'Male, patient', 'Female, patient'}, 'Location', 'best');
    ax = gca;
    ax.FontSize = 14;
    hold off;
end