clear; clc;
% load('/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/workspace.mat')

basedir = '.';
savedir = fullfile(basedir, 'results', 'final_brainmask', 'Lesion_analysis');
contdirs = dir(fullfile(basedir, 'contrasts_brainmask'));
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));
CSp_paths = fullfile(basedir, 'contrasts_brainmask', list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0011_mask.nii');
CSm_paths = fullfile(basedir, 'contrasts_brainmask', list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0012_mask.nii');
maskdir = fullfile(basedir, 'brainmask_canlab_bin_resampled.nii');
% yeodir = fullfile(savedir, 'YEO_nets');
yeodir = fullfile(savedir, 'CORR_ROIs');
% yeodir = fullfile(savedir, 'regions_boot_ROI_canlab2023');
% yeodir = fullfile(savedir, 'regions_dilated');

% yeo_nets = {'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_dmn_dil_resampled', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_dorsalatt_dil_resampled', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_frontoparietal_dil_resampled', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_limbic_dil_resampled', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_somatomotor_dil_resampled', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_ventralatt_dil_resampled', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_visual_dil_resampled'};
% yeo_nets = {'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_dmn_dil_resampled_subs', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_dorsalatt_dil_resampled_subs', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_frontoparietal_dil_resampled_subs', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_limbic_dil_resampled_subs', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_somatomotor_dil_resampled_subs', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_ventralatt_dil_resampled_subs', ...
%     'Yeo2011_7Networks_MNI152_FreeSurferConformed2mm_visual_dil_resampled_subs'};

% yeo_nets = {'brainmask_dmn', 'brainmask_dorsalatt', 'brainmask_frontoparietal_org', ...
%     'brainmask_frontoparietal', 'brainmask_limbic', 'brainmask_somatomotor', ...
%     'brainmask_ventralatt', 'brainmask_visual', 'brainmask_visual2'};

% yeo_nets = {'network_dmn', 'network_dorsalatt', 'network_frontoparietal_org', ...
%     'network_frontoparietal', 'network_limbic', 'network_somatomotor', ...
%     'network_ventralatt', 'network_visual', 'network_visual2'};

% NETS DELS CLUSTERS IMPORTANTS!!! - llista yeo sense ser yeo
yeo_nets = {'cl1_fdr05', 'cl2_fdr05', 'cl3_fdr05', 'cl4_fdr05', 'cl5_fdr05'};
% yeo_nets = {'cl1_fdr05_subs', 'cl2_fdr05_subs', 'cl3_fdr05_subs', 'cl4_fdr05_subs', 'cl5_fdr05_subs'};

% yeo_nets = {'CLUSTER1_VAR1_20_resampled_bin', 'CLUSTER1_VAR1_resampled_bin', 'CLUSTER1_VAR1_min10_20_resampled_bin', ...
%     'CLUSTER1_VAR1_min10_resampled_bin', 'CLUSTER2_VAR1_20_resampled_bin', 'CLUSTER2_VAR1_resampled_bin', ...
%     'CLUSTER3_VAR1_20_resampled_bin', 'CLUSTER3_VAR1_resampled_bin', 'CLUSTER4_VAR1_20_resampled_bin', ...
%     'CLUSTER4_VAR1_resampled_bin', 'CLUSTER5_VAR1_20_resampled_bin', 'CLUSTER5_VAR1_resampled_bin', ...
%     'CLUSTER5_VAR1_min10_20_resampled_bin', 'CLUSTER5_VAR1_min10_resampled_bin'};

% yeo_nets = {'cl1_05', 'cl1_fdr05', 'cl1_fdr05_dil', 'cl2_05', 'cl2_05_corr', 'cl2_fdr05', 'cl2_fdr05_dil', 'cl3_05', ...
%     'cl3_05_corr', 'cl3_fdr05', 'cl3_fdr05_dil', 'cl4_05', 'cl4_fdr05', 'cl4_fdr05_dil', 'cl5_05', 'cl5_fdr05',  ...
%     'cl5_fdr05_dil', 'ls_cl1_05', 'ls_cl1_fdr05', 'ls_cl1_fdr05_dil', 'ls_cl2_05', 'ls_cl2_05_corr', ...
%     'ls_cl2_fdr05', 'ls_cl2_fdr05_dil', 'ls_cl3_05', 'ls_cl3_05_corr', 'ls_cl3_fdr05', 'ls_cl3_fdr05_dil', ...
%     'ls_cl4_05', 'ls_cl4_fdr05', 'ls_cl4_fdr05_dil', 'ls_cl5_05', 'ls_cl5_fdr05', 'ls_cl5_fdr05_dil'};

%% 1. Training (80%) and test (20%) sets
% data_excel = readtable(fullfile(basedir, 'MVPA_dataset_new.xlsx'),'VariableNamingRule','preserve');
data_excel = readtable(fullfile(basedir, 'Quest_final_dataset.xlsx'),'VariableNamingRule','preserve');
% data_excel(174,:) = [];
% data_excel(173,:) = [];
% subj_names = cellfun(@(str) ['sub-' str], data_excel.ID, 'UniformOutput', false);
subj_names = cellfun(@(str) ['sub-' str], data_excel.Var1, 'UniformOutput', false);
data_excel.Properties.RowNames = subj_names;
validSubjects_var = ismember(subj_names, list_subj);

path_sets = fullfile(basedir, 'results', 'final_brainmask', '2_SVM_results_stai');
tr_set = load(fullfile(path_sets, 'training_data.mat')).tr_set;
ts_set = load(fullfile(path_sets, 'test_data.mat')).ts_set;

roc_res = array2table(zeros(length(yeo_nets), 7), 'RowNames', yeo_nets, 'VariableNames', ...
        {'Accuracy', 'Sensitivity', 'CI_i_sens', 'CI_s_sens', 'Specificity', 'CI_i_spec', 'CI_s_spec'});

for yeo = yeo_nets
    mask_yeo = fullfile(yeodir, [yeo{1} '.nii.gz']);

    training_data = fmri_data([CSp_paths(tr_set), CSm_paths(tr_set)], mask_yeo); 
    training_data.Y = [ones(sum(tr_set),1); -ones(sum(tr_set),1)];
    
    test_data = fmri_data([CSp_paths(ts_set), CSm_paths(ts_set)], mask_yeo); 
    test_data.Y = [ones(sum(ts_set),1); -ones(sum(ts_set),1)];
    
    %% 2. Developing classifiers of CS+ and CS-
    % Leave-one-subject-out cross-validation
    subject_id = [1:138, 1:138];
    
    [~, stats_CV] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', subject_id, 'error_type', 'mcr', 'dist_from_hyperplane_xval'); 
    % mcr: misclassiication rate 'dist_from_hyperplane_xval

    name = split(yeo{1}, '_');
    figure;
    ROC_CV = roc_plot(stats_CV.dist_from_hyperplane_xval, training_data.Y == 1, 'threshold', 'pairedobservations');
    x0=10; y0=10; width=900; height=800;
    set(gcf,'position', [x0, y0, width, height])
    title(['ROC curve: CS+ and CS- / only ROI: ' name{1}]) %name{5}
    saveas(gcf, fullfile(savedir, ['ROC_' yeo{1} '.png']))
    close;

    roc_res.Accuracy(yeo{1}) = ROC_CV.accuracy;
    roc_res.Sensitivity(yeo{1}) = ROC_CV.sensitivity;
    roc_res.CI_i_sens(yeo{1}) = ROC_CV.sensitivity_ci(1);
    roc_res.CI_s_sens(yeo{1}) = ROC_CV.sensitivity_ci(2);
    roc_res.Specificity(yeo{1}) = ROC_CV.specificity;
    roc_res.CI_i_spec(yeo{1}) = ROC_CV.specificity_ci(1);
    roc_res.CI_s_spec(yeo{1}) = ROC_CV.specificity_ci(2);

end

writetable(roc_res, fullfile(savedir, 'ROC_results_corr_rois.xlsx'), "WriteRowNames",true)