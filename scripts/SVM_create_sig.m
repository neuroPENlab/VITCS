clear; clc;

basedir = '/Users/acalvet/Documents/MVPA_FISAX';
savedir = fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai');
contdirs = dir(fullfile(basedir, 'DATA', 'contrasts_brainmask'));
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));
CSp_paths = fullfile(basedir, 'DATA', 'contrasts_brainmask', list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0011_mask.nii');
CSm_paths = fullfile(basedir, 'DATA','contrasts_brainmask', list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0012_mask.nii');
% CS+ / CS- = con_0011_mask / con_0012_mask
% CS+ / CS- EARLY = con_0013_mask / con_0015_mask
% CS+ / CS- LATE = con_0014_mask / con_0016_mask
maskdir = fullfile(basedir, 'DATA', 'brainmask_canlab_bin_resampled.nii');

%% 1. Training (80%) and test (20%) sets
data_excel = readtable(fullfile(basedir, 'Quest_final_dataset.xlsx'),'VariableNamingRule','preserve');

subj_names = cellfun(@(str) ['sub-' str], data_excel.Var1, 'UniformOutput', false);
data_excel.Properties.RowNames = subj_names;
validSubjects_var = ismember(subj_names, list_subj);

% edges = quantile(data_excel.STAI_T_A, 5);
% val_stratify = discretize(data_excel.STAI_T_A, [-inf, edges, inf]);
% nan_val = find(isnan(val_stratify));
% s = 3;
% for n = 1:length(nan_val)
%     val_stratify(nan_val(n)) = s;
%     if s < 6
%         s = s + 1;
%     else
%         s = 1;
%     end
% end
% val_stratify2 = val_stratify + data_excel.Sex*10;
% C = cvpartition(val_stratify2, 'HoldOut', 0.2, 'Stratify', true);
% tr_set = training(C);
% ts_set = test(C);
% save(fullfile(savedir, 'training_data.mat'), 'tr_set')
% save(fullfile(savedir, 'test_data.mat'), 'ts_set')

tr_set = load(fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai', 'training_data.mat')).tr_set;
ts_set = load(fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai', 'test_data.mat')).ts_set;

training_data = fmri_data([CSp_paths(tr_set), CSm_paths(tr_set)], maskdir); 
training_data.Y = [ones(sum(tr_set),1); -ones(sum(tr_set),1)];

test_data = fmri_data([CSp_paths(ts_set), CSm_paths(ts_set)], maskdir); 
test_data.Y = [ones(sum(ts_set),1); -ones(sum(ts_set),1)];

% Plot distributions
tr=data_excel(tr_set, :).STAI_T_A;
ts=data_excel(ts_set, :).STAI_T_A;
figure
ksdensity(data_excel(tr_set, :).STAI_T_A)
hold on
ksdensity(data_excel(ts_set, :).STAI_T_A)
legend('Train', 'Test')
xlabel('STAI\_T\_A')
ylabel('Density')
title('Kernel Density Estimate')

tr = data_excel(tr_set, :).STAI_T_A;
ts = data_excel(ts_set, :).STAI_T_A;

% KDE
[f_tr, x_tr] = ksdensity(tr);
[f_ts, x_ts] = ksdensity(ts);

figure
hold on
% Área rellena
fill(x_tr, f_tr, [0.2 0.5 0.9], 'FaceAlpha', 0.35, 'EdgeColor', [0.2 0.5 0.9], 'LineWidth', 2)
fill(x_ts, f_ts, [0.9 0.4 0.3], 'FaceAlpha', 0.35, 'EdgeColor', [0.9 0.4 0.3], 'LineWidth', 2)
box off
set(gca, 'FontSize', 18, 'LineWidth', 1)
xlabel('STAI-T')
ylabel('Density')
% title('Kernel density estimate of STAI-T distribution in training and test sets')
legend('Train', 'Test')
%% 2. Developing classifiers of CS+ and CS-

% Leave-one-subject-out cross-validation
subject_id = [1:138, 1:138];

% 10-fold CV
% subject_folds = crossvalind('Kfold', 138, 10);
% sample_folds = [subject_folds, subject_folds];
sample_folds = load(fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', '2_SVM_results_stai', '10fold_CV.mat')).sample_folds;

[~, stats_CV_10f] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', sample_folds, 'error_type', 'mcr', 'dist_from_hyperplane_xval'); 
[~, stats_CV_10f_001] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', sample_folds, 'C', 0.01, 'error_type', 'mcr', 'dist_from_hyperplane_xval'); 
[~, stats_CV_10f_01] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', sample_folds, 'C', 0.1, 'error_type', 'mcr', 'dist_from_hyperplane_xval'); 
[~, stats_CV_10f_10] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', sample_folds, 'C', 10, 'error_type', 'mcr', 'dist_from_hyperplane_xval'); 
[~, stats_CV] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', subject_id, 'error_type', 'mcr', 'dist_from_hyperplane_xval'); 
% mcr: misclassiication rate 'dist_from_hyperplane_xval
sig = stats_CV_10f.weight_obj;
sig_001 = stats_CV_10f_001.weight_obj;
sig_01 = stats_CV_10f_01.weight_obj;
sig_10 = stats_CV_10f_10.weight_obj;

sim1 = canlab_pattern_similarity(sig.dat, sig_001.dat, 'cosine_similarity');
sim2 = canlab_pattern_similarity(sig.dat, sig_01.dat, 'cosine_similarity');
sim3 = canlab_pattern_similarity(sig.dat, sig_10.dat, 'cosine_similarity');
fprintf('%.12f\n', sim1)
fprintf('%.12f\n', sim2)
fprintf('%.12f\n', sim3)

roc_plot(stats_CV_10f_001.dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');
roc_plot(stats_CV_10f_01.dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');
roc_plot(stats_CV_10f.dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');
roc_plot(stats_CV_10f_10.dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');


sig = stats_CV.weight_obj;
sig2 = stats_CV_10f.weight_obj;
canlab_pattern_similarity(sig.dat, sig2.dat, 'cosine_similarity')

% Visualizing results (pattern expression)
orthviews(stats_CV.weight_obj);
sig = stats_CV.weight_obj;
sig.fullpath = fullfile(savedir, 'svm_results_unthresholded_10foldCV.nii');
write(sig);

figure;
ROC_CV = roc_plot(stats_CV_10f.dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');
x0=10; y0=10; width=900; height=800;
set(gcf,'position', [x0, y0, width, height])
title('ROC curve: CS+ and CS-')
saveas(gcf, fullfile(savedir, 'ROC_curve_10foldCV.png'))

%% 3. Feature-level assessment - Stability (Bootstrap)
rng(12345);
[~, stats_boot] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', 1, 'error_type', 'mcr', 'bootweights', 'bootsamples', 5000); %, 'useparallel', 1
boots_threshold_fdr05 = threshold(stats_boot.weight_obj, .05, 'fdr', 'mask', maskdir);
boots_threshold_unc001 = threshold(stats_boot.weight_obj, .001, 'unc', 'mask', maskdir);
boots_threshold_unc01 = threshold(stats_boot.weight_obj, .01, 'unc', 'mask', maskdir);

path = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy';
fdr05_pos = fmri_data(fullfile(path, 'fdr05_pos.nii'), maskdir);
fdr05_neg = fmri_data(fullfile(path, 'fdr05_neg.nii'), maskdir);
unc001_pos = fmri_data(fullfile(path, 'UNC001_pos_prunedfdr05_pos.nii'), maskdir);
unc001_neg = fmri_data(fullfile(path, 'UNC001_pos_prunedfdr05_neg.nii'), maskdir);
unc01_pos = fmri_data(fullfile(path, 'UNC01_pos_prunedfdr05_pos.nii'), maskdir);
unc01_neg = fmri_data(fullfile(path, 'UNC01_pos_prunedfdr05_neg.nii'), maskdir);
clusters = fmri_data(fullfile(path, 'all_clusters.nii'), maskdir);

create_figure('lateral surfaces');
surface(clusters, 'foursurfaces', 'noverbose', 'colormap', CustomColormap2);
snapnow


orthviews(boots_threshold_fdr05);
boots_threshold_fdr05.fullpath = fullfile(savedir, 'svm_bootstrap_fdr05.nii');
write(boots_threshold_fdr05, 'thresh');

boots_threshold_unc001.fullpath = fullfile(savedir, 'svm_bootstrap_unc001.nii');
write(boots_threshold_unc001, 'thresh');

boots_threshold_unc01.fullpath = fullfile(savedir, 'svm_bootstrap_unc01.nii');
write(boots_threshold_unc01, 'thresh');


%% 4. Feature-level assessment - Importance Analysis (RFE: Recursive Feature Elimination)
% First we want to determine the number of n_finalfeat
stats_rfe_trial = svm_rfe_angels_mod(training_data, 'n_finalfeat', 1000, 'algorithm_name', 'cv_svm', 'nfolds', subject_id, 'error_type', 'mcr');
stats_rfe_trial = svm_rfe_angels_mod(training_data, 'n_removal', 100, 'n_finalfeat', 10, 'algorithm_name', 'cv_svm', 'nfolds', subject_id, 'error_type', 'mcr');

cv_acc = stats_rfe_trial.cv_accuracy;
n_feat = stats_rfe_trial.n_features;
idx_max10000 = 1:find(n_feat == 10017);
idx_change = [find(diff(cv_acc(idx_max10000)) ~= 0) + 1; length(idx_max10000)];

fig=figure;
plot(n_feat(idx_max10000), cv_acc(idx_max10000), 'linewidth', 2)
hold on;
scatter(n_feat(idx_change), cv_acc(idx_change), 'linewidth', 3)
x0=10; y0=10; width=5000; height=600;
set(gcf,'position', [x0, y0, width, height])
set(gca, 'XDir', 'reverse');
grid on;
ax = gca;
ax.XAxis.Exponent = 0; % Desactiva la notación científica
xtickformat('%d');
ylim([0.75, 1]);
xlim([10000, max(n_feat(idx_change))]);
% xticks(sort(stats_rfe_trial.n_features, 'ascend')); % Asegura que todas las features se etiqueten
% xtickangle(45);
xlabel('Number of features')
ylabel('Accuracy')
fontsize(fig, 16, "points")
title('Number of features vs accuracy (RFE analysis)', 'FontSize', 20)
saveas(gcf, fullfile(savedir, 'Imortance_analysis_Nfeatvsacc_bona.png'))
close;