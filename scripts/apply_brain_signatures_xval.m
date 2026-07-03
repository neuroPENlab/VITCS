clear; clc;
basedir = '/Users/acalvet/Documents/MVPA_FISAX';
save_results = fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai');
maskdir = fullfile(basedir, 'DATA', 'brainmask_canlab_bin_resampled.nii');
% maskdir = fullfile(basedir, 'DATA', 'neurosynth_masks', 'neurosynth_mask_final', ...
%     'neurosynth_mask_open2_dil2_resampled_dmn_somamotor2.nii');

contdirs = dir(fullfile(basedir, 'DATA', 'contrasts_brainmask'));
subj_names = {contdirs([contdirs.isdir]).name};
subj_names = subj_names(~ismember(subj_names, {'.', '..'}))';
load(fullfile(save_results, 'test_data.mat'));
subj_ts = subj_names(ts_set);
% subj_names = subj_names(ts_set);
% contrast_files = {{'con_0011_mask'; 'con_0012_mask'; 'con_0001_mask'}, {'con_0013_mask'; 'con_0014_mask'; 'con_0015_mask'; 'con_0016_mask'}, ...
%     {'con_0017_mask'; 'con_0018_mask'}, {'con_0019_mask'; 'con_0020_mask'; 'con_0021_mask'; 'con_0022_mask'}};
% contrast_names = {{'CS+', 'CS-', 'CS+CS-'}, {'CS+early', 'CS+late', 'CS-early', 'CS-late'}, ...
%     {'CS+rev', 'CS-rev'}, {'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'}};

contrast_files = {{'con_0011_mask'; 'con_0012_mask'}, {'con_0001_mask'}, {'con_0013_mask'; 'con_0014_mask'; 'con_0015_mask'; 'con_0016_mask'}, ...
    {'con_0017_mask'; 'con_0018_mask'}, {'con_0019_mask'; 'con_0020_mask'; 'con_0021_mask'; 'con_0022_mask'}};
contrast_names = {{'CS+', 'CS-'}, {'CS+>CS-'}, {'CS+early', 'CS+late', 'CS-early', 'CS-late'}, ...
    {'CS+rev', 'CS-rev'}, {'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'}};

metric = 'dot_product'; % dot_product cosine_similarity
%% Load brain signatures
load(fullfile(save_results, 'stats_CV.mat'));
load(fullfile(save_results, 'training_data.mat'));
% Calculate pattern expression and save results
res_pat_exp = array2table(zeros(length(subj_names), 13), 'VariableNames', reshape([contrast_names{:}]', [], 1));
res_pat_exp.Properties.RowNames = subj_names;
s_train = 1;
for s = 1:length(subj_names)
    subj = subj_names{s};
    if tr_set(s) == 1
        sig_xval = fmri_data(maskdir);
        sig_xval.dat = stats_CV.other_output_cv{s_train,1};
        s_train = s_train + 1;
    else
        sig_xval = fmri_data(fullfile(save_results, 'svm_results_unthresholded.nii'), maskdir);
    end
    for C = 1:length(contrast_files)
        clear data_obj_orig pat_exp contrast_file contrast_name;
        contrast_file = contrast_files{C};
        contrast_name = contrast_names{C};
        % Calculate pattern expression
        for i = 1:length(contrast_file)
            path_img = fullfile(basedir, 'DATA', 'contrasts_brainmask', subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', [contrast_file{i} '.nii']);
            data_obj_orig = fmri_data(path_img, maskdir);
        
            data_obj = resample_space(data_obj_orig, sig_xval);
            pat_exp{i} = canlab_pattern_similarity(data_obj.dat, sig_xval.dat, metric);
        end

        % Table for pattern expression values
        if length(contrast_name) == 2
            res_pat_exp{subj, contrast_name{1}} = pat_exp{1};
            res_pat_exp{subj, contrast_name{2}} = pat_exp{2};
        elseif length(contrast_name) == 3
            res_pat_exp{subj, contrast_name{1}} = pat_exp{1};
            res_pat_exp{subj, contrast_name{2}} = pat_exp{2};
            res_pat_exp{subj, contrast_name{3}} = pat_exp{3};
        elseif isscalar(contrast_name)
            res_pat_exp{subj, contrast_name{1}} = pat_exp{1};
        else
            res_pat_exp{subj, contrast_name{1}} = pat_exp{1};
            res_pat_exp{subj, contrast_name{2}} = pat_exp{2};
            res_pat_exp{subj, contrast_name{3}} = pat_exp{3};
            res_pat_exp{subj, contrast_name{4}} = pat_exp{4};
        end
    end
end

% writetable(res_pat_exp, fullfile(save_results, 'pat_exp_late_all_data_xval.xlsx'), 'WriteRowNames', true);

%% PLOT
for C = 1:length(contrast_files)
    contrast_name = contrast_names{C};
    if contains(contrast_name{1}, 'rev'); rev = 'Reversal'; else; rev = 'Conditioning'; end
    if contains(contrast_name{1}, 'early'); ea = 'earlylate'; else; ea = ''; end
    if length(contrast_name) == 2
        colors = {[.4 .6 1], [1 1 0]};
    elseif length(contrast_name) == 3
        colors = {[.4 .6 1], [0 0 .7], [1 1 0]};
    else  % early/late
        colors = {[.4 .6 1], [0 0 .7], [1 1 0], [1 .7 0]};
    end
    % Violin plots
    figure;
    barplot_columns_angels(res_pat_exp{subj_ts,contrast_name}, 'nofigure', 'colors', colors, 'names', contrast_name, 'dolines');
    set(gca, 'FontSize', 34)
    ylabel('Pattern expression');
    xlabel('');
    ylim([-3, 6.5]);
    % ylabel(strrep(metric, '_', ' '));
    % title(strrep([rev ' Test set'], '_', ' '))
    title('Acquisition Test set'); % Reversal Acquisition
    x0=10; y0=10; width=800; height=650;
    set(gcf,'position', [x0, y0 , width, height])
    % saveas(gcf, fullfile(save_results, ['CS+CS-' rev ea '_test_xval_bo2.png']))

end

%% PLOT ARTICLE -- ROC CURVES TOGETHER!
load(fullfile(save_results, 'stats_CV.mat'));

cont_cond = contrast_names{1};
cont_rev = contrast_names{3};

tr_subj = subj_names(tr_set);
ts_subj = subj_names(ts_set);

% Definim colors pastel en RGB (0-1)
col1 = [239,  83,  80, 255] / 255;  % coral vermellós
col2 = [ 63,  81, 181, 255] / 255;  % blau indigo
col3 = [ 38, 166, 154, 255] / 255;  % verd aigua

figure;
r1 = roc_plot(stats_CV.dist_from_hyperplane_xval, stats_CV.Y == 1, ...
    'threshold', 'pairedobservations', 'color', col1);
hold on;
r2 = roc_plot([res_pat_exp{ts_subj,cont_cond{1}}; res_pat_exp{ts_subj,cont_cond{2}}], ...
    [ones(length(res_pat_exp{ts_subj,cont_cond{1}}),1); zeros(length(res_pat_exp{ts_subj,cont_cond{2}}),1)], ...
    'threshold', 'pairedobservations', 'color', col2);
hold on;
r3 = roc_plot([res_pat_exp{ts_subj,cont_rev{1}}; res_pat_exp{ts_subj,cont_rev{2}}], ...
    [ones(length(res_pat_exp{ts_subj,cont_rev{1}}),1); zeros(length(res_pat_exp{ts_subj,cont_rev{2}}),1)], ...
    'threshold', 'pairedobservations', 'color', col3);
hold off;
x0=10; y0=10; width=500; height=450;
title('ROC plot', 'FontSize', 30)
% Augmentar el gruix de les línies
r1.line_handle(2).LineWidth = 3;
r2.line_handle(2).LineWidth = 3;
r3.line_handle(2).LineWidth = 3;
lgd = legend([r1.line_handle(2), r2.line_handle(2), r3.line_handle(2)], ...
    {'CV - Training set', 'Acquisition Test set', 'Reversal Test set'}, ...
    'Location','southeast');
lgd.FontSize = 21; % mida de la llegenda
set(gca, 'FontSize', 28)
set(gcf,'position', [x0, y0, width, height])
% saveas(gcf, fullfile(save_results, ['ROC_all_data_' rev ea '_xval.png']))

