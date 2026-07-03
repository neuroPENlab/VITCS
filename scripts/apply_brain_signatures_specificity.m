clear; clc;
basedir = '/Users/acalvet/Documents/MVPA_FISAX';
save_results = fullfile(basedir,'TFM_git', 'results', 'final_brainmask', 'VITCS_specificity');
maskdir = fullfile(basedir, 'DATA', 'brainmask_canlab_bin_resampled.nii');

metric = 'dot_product';
% metric = 'cosine_similarity';

contrast_dir = fullfile(save_results, 'stats_paper_baseline');
contrast_dir = fullfile(save_results, 'stats_paper');
list_subj = {'RCPNS_04', 'RCPNS_05', 'RCPNS_09', 'RCPNS_12', 'RCPNS_15', 'RCPNS_16', 'RCPNS_19', 'RCPNS_21', 'RCPNS_28',...
    'RCPNS_31', 'RCPNS_35', 'RCPNS_36', 'RCPNS_38', 'RCPNS_39', 'RCPNS_40', 'RCPNS_42', 'RCPNS_44', 'RCPNS_45', 'RCPNS_46', ...
    'RCPNS_48', 'RCPNS_50', 'RCPNS_51', 'RCPNS_54', 'RCPNS_55', 'RCPNS_60', 'RCPNS_61', 'RCPNS_62', 'RCPNS_69', 'RCPNS_70',...
    'RCPNS_77', 'RCPNS_83', 'RCPNS_85', 'RCPNS_88', 'RCPNS_89', 'RCPNS_90', 'RCPNS_92', 'RCPNS_100', 'RCPNS_101', 'RCPNS_102'};

%% Load brain signatures
vitcs = fmri_data(fullfile(basedir,'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai', 'svm_results_unthresholded.nii'), maskdir);

%% Calculate pattern expression and save results
gain_paths = fullfile(contrast_dir, list_subj, 'stats_mid_2026', 'con_0003.nii');
loss_paths = fullfile(contrast_dir, list_subj, 'stats_mid_2026', 'con_0004.nii');
cuegain_paths = fullfile(contrast_dir, list_subj, 'stats_mid_2026', 'con_0005.nii');
cueloss_paths = fullfile(contrast_dir, list_subj, 'stats_mid_2026', 'con_0006.nii');
% fixation_paths = fullfile(contrast_dir, list_subj, 'stats_mid_2026', 'con_0008.nii');

data_gain = fmri_data(gain_paths, maskdir); 
data_loss = fmri_data(loss_paths, maskdir); 
data_cuegain = fmri_data(cuegain_paths, maskdir); 
data_cueloss = fmri_data(cueloss_paths, maskdir); 
% data_fixation = fmri_data(fixation_paths, maskdir); 

% Calculate pattern expression
vitcs_resampled = resample_space(vitcs, data_gain);
pat_exp(:, 1) = canlab_pattern_similarity(data_gain.dat, vitcs_resampled.dat, metric);
pat_exp(:, 2) = canlab_pattern_similarity(data_loss.dat, vitcs_resampled.dat, metric);
pat_exp(:, 3) = canlab_pattern_similarity(data_cuegain.dat, vitcs_resampled.dat, metric);
pat_exp(:, 4) = canlab_pattern_similarity(data_cueloss.dat, vitcs_resampled.dat, metric);
% pat_exp(:, 5) = canlab_pattern_similarity(data_fixation.dat, vitcs_resampled.dat, metric);


% Table for pattern expression values
% res_pat_exp = array2table(pat_exp, 'VariableNames', {'gain', 'loss', 'cuegain', 'cueloss', 'fixation'});
res_pat_exp = array2table(pat_exp, 'VariableNames', {'gain', 'loss', 'cuegain', 'cueloss'});
res_pat_exp.Properties.RowNames = list_subj;

% Violin plots
colors = {[1 1 0], [.4 .6 1]};
% contrast_name = {'gain', 'loss'};
contrast_name = {'cuegain', 'cueloss'};
% contrast_name = {'gain', 'fixation'};
% contrast_name = {'cuegain', 'fixation'};

figure;
barplot_columns_angels(res_pat_exp{:, contrast_name}, 'nofigure', 'colors', colors, 'names', contrast_name, 'dolines');
set(gca, 'FontSize', 20)
ylabel('Pattern expression');
xlabel('');
ylabel(strrep(metric, '_', ' '));
title([contrast_name{1} ' vs ' contrast_name{2}])
x0=10; y0=10; width=800; height=650;
set(gcf,'position', [x0, y0 , width, height])
% saveas(gcf, fullfile(save_results, [contrast_name{1} '_' contrast_name{2} '_dot.png']))

roc_mid = roc_plot([res_pat_exp{:, contrast_name{1}}; res_pat_exp{:, contrast_name{2}}], [ones(size(res_pat_exp, 1),1);...
    zeros(size(res_pat_exp, 1),1)], 'threshold', 'pairedobservations');

% Cohen's D
dif_mid = res_pat_exp{:, contrast_name{1}} - res_pat_exp{:, contrast_name{2}};
d = mean(dif_mid)/std(dif_mid);

% One sample t-test
[h, p, ci, stats] = ttest(dif_mid);
% BF con función de CANlab o con la de Rouder directamente
t  = stats.tstat;
N  = length(dif_mid);

t1smpbf(t, N)

%% Tor data (HCP)
load(fullfile(save_results, 'Tor_HCP', 'VITCS_scores_HCP_wager.mat'))

% Calculate accuracy
reward_v_punish = VITCS_scores.condition_scores{2};
tom_v_random = VITCS_scores.condition_scores{8};

reward_v_punish_cos = VITCS_scores.condition_scores_cosine{2};
tom_v_random_cos = VITCS_scores.condition_scores_cosine{8};

% Forced-choice analysis
roc_rew_punish = roc_plot([reward_v_punish(:,1); reward_v_punish(:,2)], [ones(size(reward_v_punish, 1),1);...
    zeros(size(reward_v_punish, 1),1)], 'threshold', 'pairedobservations');
roc_rew_punish_cos = roc_plot([reward_v_punish_cos(:,1); reward_v_punish_cos(:,2)], [ones(size(reward_v_punish_cos, 1),1);...
    zeros(size(reward_v_punish_cos, 1),1)], 'threshold', 'pairedobservations');

roc_tom = roc_plot([tom_v_random(:,1); tom_v_random(:,2)], [ones(size(tom_v_random, 1),1);...
    zeros(size(tom_v_random, 1),1)], 'threshold', 'pairedobservations');
roc_tom_cos = roc_plot([tom_v_random_cos(:,1); tom_v_random_cos(:,2)], [ones(size(tom_v_random_cos, 1),1);...
    zeros(size(tom_v_random_cos, 1),1)], 'threshold', 'pairedobservations');

dif_reward = reward_v_punish(:,1) - reward_v_punish(:,2);
dif_reward_cos = reward_v_punish_cos(:,1) - reward_v_punish_cos(:,2);
dif_tom = tom_v_random(:,1) - tom_v_random(:,2);
dif_tom_cos = tom_v_random_cos(:,1) - tom_v_random_cos(:,2);

% One sample t-test
[h, p, ci, stats] = ttest(dif_reward);
% BF con función de CANlab o con la de Rouder directamente
t  = stats.tstat;
N  = length(dif_reward);

t1smpbf(t, N)
