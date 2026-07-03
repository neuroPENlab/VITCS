clear; clc;
basedir = '.';
infodir = fullfile(basedir, 'results', 'final_brainmask', 'Mult_log_regression');
savedir = fullfile(basedir, 'results', 'final_brainmask', 'SVM_anxiety');
contdirs = dir(fullfile(basedir, 'contrasts_brainmask'));
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));

maskdir = fullfile(basedir, 'brainmask_canlab_bin_resampled.nii');
graydir = fullfile(basedir, 'gray_matter_mask_canlab_bin_resampled_lineal_bin.nii');

contrast_files = {'con_0011_mask', 'con_0012_mask', 'con_0001_mask', 'con_0013_mask', 'con_0014_mask',...
    'con_0015_mask', 'con_0016_mask', 'con_0017_mask', 'con_0018_mask', ...
    'con_0019_mask', 'con_0020_mask', 'con_0021_mask', 'con_0022_mask'};
contrast_names = {'CS+', 'CS-', 'CS+CS-', 'CS+early', 'CS+late', 'CS-early', 'CS-late', ...
    'CS+rev', 'CS-rev', 'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'};
%% 1. Training (100%)
int_vars = {'DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'STAI_T_A', 'SCSR_P_A', 'EMA_2weeks_first'};
% int_vars = {'pca_all_tertil', 'pca_without_EMA_tertil', 'pca_only_DASSA_STAI_SCSRP_tertil'};
int_var_names = {'all', 'without_EMA', 'only_DASSA_STAI_SCSRP'};

for i = 1:length(int_vars)
    int_var = int_vars{i};
    int_var_name = int_var_names{i};
    
    data_excel = readtable(fullfile(infodir, [int_var '_patexp.xlsx']),'VariableNamingRule','preserve');
    data_excel.Properties.RowNames = data_excel.(data_excel.Properties.VariableNames{1});
    data_excel(:, data_excel.Properties.VariableNames{1}) = [];
    validSubjects_var = data_excel.Properties.RowNames;
    
    figure;
    histogram(data_excel.(int_var_name), 20);
    title(['Data set distribution (N = ' num2str(length(data_excel.(int_var_name))) ')']);
    xlabel([int_var ' value']);
    ylabel('Frequency');
    set(gca, 'FontSize', 14)
    x0=500; y0=500; width=600; height=400;
    set(gcf,'position', [x0, y0, width, height])
    saveas(gcf, fullfile(savedir, ['Dist_' int_var '2.png']))
    close;
    % 2. Developing classifiers
    
    roc_res = array2table(zeros(length(contrast_files), 7), 'RowNames', contrast_names, 'VariableNames', ...
        {'Accuracy', 'Sensitivity', 'CI_i_sens', 'CI_s_sens', 'Specificity', 'CI_i_spec', 'CI_s_spec'});
    for c = 1:length(contrast_files)
        CS_paths = fullfile(basedir, 'contrasts_brainmask', validSubjects_var, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', [contrast_files{c} '.nii']);
    
        % Leave-one-subject-out cross-validation
        subject_id = 1:length(data_excel.(int_var_name));
        data = fmri_data(CS_paths);
        data.Y = data_excel.IQ;
        [~, stats_CV] = predict(data, 'algorithm_name', 'cv_svm', 'nfolds', subject_id, 'error_type', 'mcr', 'dist_from_hyperplane_xval'); 
        % mcr: misclassiication rate 'dist_from_hyperplane_xval
        % save(fullfile(savedir, ['stats_CV_' int_var '_' contrast_names{c} '.mat']), 'stats_CV')
    
        % Visualizing results (pattern expression)
        % orthviews(stats_CV.weight_obj);
        sig = stats_CV.weight_obj;
        sig.fullpath = fullfile(savedir, 'svm_results_unthresholded.nii');
        % write(sig);
    
        % [~, stats_boot] = predict(data, 'algorithm_name', 'cv_svm', 'nfolds', 1, 'error_type', 'mcr', 'bootweights', 'bootsamples', 5000, 'useparallel', 1);
        % maskdir = fullfile(basedir, 'brainmask_canlab_bin_resampled.nii');
        % boots_threshold_BM = threshold(stats_boot.weight_obj, .05, 'fdr', 'mask', maskdir, 'k', 10);
        % boots_threshold_BM.fullpath = fullfile(savedir, 'boots_fdr05_k10.nii');
        % write(boots_threshold_BM, 'thresh');
        % orthviews(boots_threshold_BM);
    
        figure;
        ROC_CV = roc_plot(stats_CV.dist_from_hyperplane_xval, data.Y == 1, 'threshold', 0);
        x0=10; y0=10; width=900; height=800;
        set(gcf,'position', [x0, y0, width, height])
        title(['ROC curve ' int_var ' ' contrast_names{c}])
        saveas(gcf, fullfile(savedir, ['ROC_' int_var '_' contrast_names{c} '2.png']))
        close;
        
        roc_res.Accuracy(contrast_names{c}) = ROC_CV.accuracy;
        roc_res.Sensitivity(contrast_names{c}) = ROC_CV.sensitivity;
        roc_res.CI_i_sens(contrast_names{c}) = ROC_CV.sensitivity_ci(1);
        roc_res.CI_s_sens(contrast_names{c}) = ROC_CV.sensitivity_ci(2);
        roc_res.Specificity(contrast_names{c}) = ROC_CV.specificity;
        roc_res.CI_i_spec(contrast_names{c}) = ROC_CV.specificity_ci(1);
        roc_res.CI_s_spec(contrast_names{c}) = ROC_CV.specificity_ci(2);
    end
    
    writetable(roc_res, fullfile(savedir, ['ROC_' int_var '.xlsx']), "WriteRowNames",true)

end