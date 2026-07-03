clear; clc;
basedir = '/Users/acalvet/Documents/MVPA_FISAX';
save_results = fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', '1_sig_evaluation');
maskdir = fullfile(basedir, 'DATA', 'brainmask_canlab_bin_resampled.nii');

contdirs = dir(fullfile(basedir, 'DATA', 'contrasts_brainmask'));
subj_names = {contdirs([contdirs.isdir]).name};
subj_names = subj_names(~ismember(subj_names, {'.', '..'}))';

% contrast_files = {{'con_0011_mask'; 'con_0012_mask'; 'con_0001_mask'}, {'con_0013_mask'; 'con_0014_mask'; 'con_0015_mask'; 'con_0016_mask'}, ...
%     {'con_0017_mask'; 'con_0018_mask'}, {'con_0019_mask'; 'con_0020_mask'; 'con_0021_mask'; 'con_0022_mask'}};
% contrast_names = {{'CS+', 'CS-', 'CS+CS-'}, {'CS+early', 'CS+late', 'CS-early', 'CS-late'}, ...
%     {'CS+rev', 'CS-rev'}, {'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'}};

contrast_files = {{'con_0011_mask'; 'con_0012_mask'}, {'con_0013_mask'; 'con_0015_mask'; 'con_0014_mask'; 'con_0016_mask'}, ...
    {'con_0017_mask'; 'con_0018_mask'}, {'con_0019_mask'; 'con_0021_mask'; 'con_0020_mask'; 'con_0022_mask'}};
contrast_names = {{'CS+', 'CS-'}, {'CS+early', 'CS-early', 'CS+late', 'CS-late'}, ...
    {'CS+rev', 'CS-rev'}, {'CS+revearly', 'CS-revearly', 'CS+revlate', 'CS-revlate'}};

metric = 'dot_product'; % dot_product
evaluation = 2;

%% Load brain signatures
% [threat, ] = load_image_set({fullfile(basedir, 'DATA', 'brainsignatures', 'IE_ImEx_Acq_Threat_SVM_nothresh.nii')});
% [suitas, ] = load_image_set({fullfile(basedir, 'DATA', 'brainsignatures', 'Induced20_z.nii')});
% [pines, ] = load_image_set({fullfile(basedir, 'DATA', 'brainsignatures', 'Rating_Weights_LOSO_2.nii')});
% [vifs, ] = load_image_set({fullfile(basedir, 'DATA', 'brainsignatures', 'VIFS.nii')});
% [wen, ] = load_image_set({fullfile(basedir, 'DATA', 'brainsignatures', 'cond_1block_predictive_map_raw.nii')});
[reddan, ] = load_image_set({fullfile(save_results, 'signatures', 'IE_ImEx_Acq_Threat_SVM_nothresh.nii')});
% [suitas, ] = load_image_set({fullfile(save_results, 'signatures', '3_Liu_SUITAS_Induced20_z.nii')});

if evaluation == 1 % TEST DATA
    own_sig = fmri_data(fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', ...
        '2_SVM_results_stai_late', 'svm_results_unthresholded.nii'), maskdir);
    % signatures = {own_sig, threat, suitas, pines, vifs};
    % sig_names = {'VITS', 'Threat', 'SUITAS', 'PINES', 'VIFS'};
    signatures = {own_sig};
    sig_names = {'VITS'};

    test_subj = load(fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai', 'test_data.mat')).ts_set;
    subj_names = subj_names(test_subj);
elseif evaluation == 2 % ALL DATA
    % own_sig = fmri_data(fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', ...
    %     '2_SVM_results_stai_neurosynth', 'svm_results_unthresholded2.nii'), maskdir);
    % signatures = {own_sig, threat, suitas, pines, vifs};
    % sig_names = {'VITS', 'Threat', 'SUITAS', 'PINES', 'VIFS'};
    % signatures = {own_sig};
    % sig_names = {'VITS'};
    signatures = {reddan};
    sig_names = {'reddan'};
else
    signatures = {threat, suitas, pines, vifs};
    sig_names = {'Threat', 'SUITAS', 'PINES', 'VIFS'};
end

%% Calculate pattern expression and save results
for C = 1:length(contrast_files)
    clear data_obj_orig pat_exp res_pat_exp res_ttest res_2AFC contrast_file contrast_name col row_names;
    contrast_file = contrast_files{C};
    contrast_name = contrast_names{C};
    if contains(contrast_name{1}, 'rev'); rev = 'rev'; else; rev = ''; end
    if contains(contrast_name{1}, 'early'); ea = 'earlylate'; else; ea = ''; end
    % Calculate pattern expression
    for i = 1:length(contrast_file)
        path_img = fullfile(basedir, 'DATA', 'contrasts_brainmask', subj_names, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', [contrast_file{i} '.nii']);
        data_obj = fmri_data(path_img, maskdir);
    
        for s = 1:length(signatures)
            sig_resampled = resample_space(signatures{s}, data_obj);
            pe(:, s) = canlab_pattern_similarity(data_obj.dat, sig_resampled.dat, metric);
        end
        pat_exp{i} = pe;
    end
    % Table for pattern expression values
    i = 1;
    j = 1;
    for sig = sig_names
        for name = contrast_name
            col{i} = [sig{1} '_' name{1}];
            i = i + 1;
        end
        if length(contrast_name) > 3 % early/late = {'CS+early', 'CS+late', 'CS-early', 'CS-late'}
            col{i} = [sig{1} '_' contrast_name{1} '_' contrast_name{2} '_diff'];
            i = i + 1;
            row_names{j} = [sig{1} '_' contrast_name{1} '_' contrast_name{2}];
            j = j + 1;
            col{i} = [sig{1} '_' contrast_name{3} '_' contrast_name{4} '_diff'];
            i = i + 1;
            row_names{j} = [sig{1} '_' contrast_name{3} '_' contrast_name{4}];
            j = j + 1;
        else
            col{i} = [sig{1} '_diff'];
            i = i + 1;
        end
    end
    res_pat_exp = array2table(zeros(length(subj_names), length(col)), 'VariableNames', col);
    res_pat_exp.Properties.RowNames = subj_names;
    
    % Table for t-test and 2-alternative forced-choice results
    if length(contrast_name) == 2
        row_names = sig_names;
        colors = {[.4 .6 1], [1 1 0]};
    elseif length(contrast_name) == 3
        row_names = sig_names;
        colors = {[.4 .6 1], [0 0 .7], [1 1 0]};
    else  % early/late
        colors = {[.4 .6 1], [0 0 .7], [1 1 0], [1 .7 0]};
    end
    
    res_ttest = array2table(zeros(length(row_names), 7), 'VariableNames', {'p', 'ci_l', 'ci_h', 'tstat', 'df', 'sd', 'cohend'});
    res_ttest.Properties.RowNames = row_names;
    res_2AFC = array2table(zeros(length(row_names), 3), 'VariableNames', {'TP', 'N', 'acc'});
    res_2AFC.Properties.RowNames = row_names;
    
    for s = 1:length(sig_names)
        pat_exp_s = cellfun(@(x) x(:, s), pat_exp, 'UniformOutput', false); 
        % figure;
        % barplot_columns_angels(pat_exp_s, 'nofigure', 'colors', colors, 'names', contrast_name, 'dolines');
        % set(gca, 'FontSize', 20)
        % ylabel(strrep(metric, '_', ' '));
        % title(strrep([metric ' ' sig_names{s} ', CS+ CS-' ea ' ' rev], '_', ' '))
        % x0=10; y0=10; width=1200; height=1000;
        % set(gcf,'position', [x0, y0, width, height])
        % saveas(gcf, fullfile(save_results, ['CS+CS-' rev ea '_' sig_names{s} '_all_sample.png']))
    
        % Pattern expression
        if length(contrast_name) == 2
            res_pat_exp{:, [sig_names{s} '_' contrast_name{1}]} = pat_exp_s{1};
            res_pat_exp{:, [sig_names{s} '_' contrast_name{2}]} = pat_exp_s{2};
        elseif length(contrast_name) == 3
            res_pat_exp{:, [sig_names{s} '_' contrast_name{1}]} = pat_exp_s{1};
            res_pat_exp{:, [sig_names{s} '_' contrast_name{2}]} = pat_exp_s{2};
            res_pat_exp{:, [sig_names{s} '_' contrast_name{3}]} = pat_exp_s{3};
        else
            res_pat_exp{:, [sig_names{s} '_' contrast_name{1}]} = pat_exp_s{1};
            res_pat_exp{:, [sig_names{s} '_' contrast_name{2}]} = pat_exp_s{2};
            res_pat_exp{:, [sig_names{s} '_' contrast_name{3}]} = pat_exp_s{3};
            res_pat_exp{:, [sig_names{s} '_' contrast_name{4}]} = pat_exp_s{4};
        end
    end
    for r = 1:length(row_names)
        if length(contrast_name) < 4
            pat_exp_s = cellfun(@(x) x(:, r), pat_exp, 'UniformOutput', false);
        elseif r == 1 || r == 2
            pat_exp_s = cellfun(@(x) x(:, 1), pat_exp, 'UniformOutput', false);
        elseif r == 3 || r == 4
            pat_exp_s = cellfun(@(x) x(:, 2), pat_exp, 'UniformOutput', false);
        elseif r == 5 || r == 6
            pat_exp_s = cellfun(@(x) x(:, 3), pat_exp, 'UniformOutput', false);
        elseif r == 7 || r == 8
            pat_exp_s = cellfun(@(x) x(:, 4), pat_exp, 'UniformOutput', false);
        end
        % Paired-sample t-test (within-subjects t-test)
        if contains(row_names{r}, ['-' rev 'early']) && contains(row_names{r}, ['-' rev 'late'])
            [h, res_ttest{row_names{r}, 'p'}, ci, stats] = ttest(pat_exp_s{3}, pat_exp_s{4});
            if pat_exp_s{3} - pat_exp_s{4} ~= 0
                diff_val = (pat_exp_s{3} - pat_exp_s{4})./(pat_exp_s{3} + pat_exp_s{4});
            else
                diff_val = NaN;
            end
        else
            [h, res_ttest{row_names{r}, 'p'}, ci, stats] = ttest(pat_exp_s{1}, pat_exp_s{2});
            if pat_exp_s{1} - pat_exp_s{2} ~= 0
                diff_val = (pat_exp_s{1} - pat_exp_s{2})./(pat_exp_s{1} + pat_exp_s{2});
            else 
                diff_val = NaN;
            end
        end
        res_ttest{row_names{r}, 'ci_l'} = ci(1);
        res_ttest{row_names{r}, 'ci_h'} = ci(2);
        res_ttest{row_names{r}, 'tstat'} = stats.tstat;
        res_ttest{row_names{r}, 'df'} = stats.df;
        res_ttest{row_names{r}, 'sd'} = stats.sd;
        % + Cohen's d
        res_ttest{row_names{r}, 'cohend'} = mean(diff_val) / std(diff_val);
    
        % 2-alternative forced choice (2AFC)
        if strcmp(ea, 'earlylate')
            res_2AFC(row_names{r}, :) = [];
        else
            res_2AFC{row_names{r}, 'TP'} = sum(diff_val>0); % CS+ - CS- > 0
            res_2AFC{row_names{r}, 'N'} = length(diff_val);
            res_2AFC{row_names{r}, 'acc'} = res_2AFC{row_names{r}, 'TP'}/res_2AFC{row_names{r}, 'N'};
        end
    
        % Pattern expression difference
        res_pat_exp{:, [row_names{r} '_diff']} = diff_val;
    end
    
    writetable(res_pat_exp, fullfile(save_results, ['CS+CS-' rev ea '_pat_exp_reddan.xlsx']), 'WriteRowNames', true);
    % writetable(res_ttest, fullfile(save_results, ['CS+CS-' rev ea '_ttest_all_sample.xlsx']), 'WriteRowNames', true);
    if strcmp(ea, '')
        % writetable(res_2AFC, fullfile(save_results, ['CS+CS-' rev ea '_2AFC_all_sample.xlsx']), 'WriteRowNames', true);
    end
end

%%
sig_names = {'Our_sig', 'Threat', 'SUITAS', 'PINES', 'VIFS'};

contrast_names = {{'CS+', 'CS-', 'CS+CS-'}, {'CS+early', 'CS+late', 'CS-early', 'CS-late'}, ...
    {'CS+rev', 'CS-rev'}, {'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'}};


figure;
ROC_CV = roc_plot([pat_exp{1}; pat_exp{2}], [ones(length(pat_exp{1}),1);...
    zeros(length(pat_exp{2}),1)], 'threshold', 'pairedobservations');
x0=10; y0=10; width=900; height=800;
title({'ROC curve: CS+ rev, CS- rev (test set)'})
set(gcf,'position', [x0, y0, width, height])
saveas(gcf, '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/SVM_results_late_same/ROC_CS+CS-revearly.png')


figure;
ROC_CV = roc_plot([pat_exp{1}(:,3); pat_exp{2}(:,3)], [ones(length(pat_exp{1}(:,3)),1);...
    zeros(length(pat_exp{2}(:,3)),1)], 'threshold', 'pairedobservations');
x0=10; y0=10; width=900; height=800;
set(gcf,'position', [x0, y0, width, height])
saveas(gcf, '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/3_sig_evaluation_test/ROC_plots/ROC_rev_SUITAS.png')