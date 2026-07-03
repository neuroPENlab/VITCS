clear; clc;
basedir = '/Users/acalvet/Documents/MVPA_FISAX';
infodir = fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', 'Mult_log_regression', 'PATTERN_EXPRESSION_late');
savedir = fullfile(basedir, 'TFM_git', 'results', 'final_brainmask', 'SVM_anxiety_patexp_late', 'feature_selection');
% infodir = fullfile(basedir, 'results', 'final_brainmask', 'Mult_log_regression', 'SKIN_CONDUCTANCE');
% savedir = infodir;
contdirs = dir(fullfile(basedir, 'DATA', 'contrasts_brainmask'));
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));

% contrast_files = {{'VITS_CS+early', 'VITS_CS+late', 'VITS_CS-early', 'VITS_CS-late'},...
%     {'VITS_CS+revearly', 'VITS_CS+revlate', 'VITS_CS-revearly', 'VITS_CS-revlate'},...
%     {'VITS_CS+early', 'VITS_CS+late', 'VITS_CS-early', 'VITS_CS-late', ...
%     'VITS_CS+revearly', 'VITS_CS+revlate', 'VITS_CS-revearly', 'VITS_CS-revlate'},...
%     {'VITS_CS+', 'VITS_CS-', 'VITS_CS+early', 'VITS_CS+late', 'VITS_CS-early', 'VITS_CS-late'},...
%     {'VITS_CS+rev', 'VITS_CS-rev', 'VITS_CS+revearly', 'VITS_CS+revlate', 'VITS_CS-revearly', 'VITS_CS-revlate'},...
%     {'VITS_CS+', 'VITS_CS-', 'VITS_CS+early', 'VITS_CS+late', 'VITS_CS-early', 'VITS_CS-late', ...
%     'VITS_CS+rev', 'VITS_CS-rev', 'VITS_CS+revearly', 'VITS_CS+revlate', 'VITS_CS-revearly', 'VITS_CS-revlate'}};
contrast_files = {{'CS+early', 'CS+late', 'CS-early', 'CS-late'},...
    {'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'},...
    {'CS+early', 'CS+late', 'CS-early', 'CS-late', ...
    'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'},...
    {'CS+', 'CS-', 'CS+early', 'CS+late', 'CS-early', 'CS-late'},...
    {'CS+rev', 'CS-rev', 'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'},...
    {'CS+', 'CS-', 'CS+early', 'CS+late', 'CS-early', 'CS-late', ...
    'CS+rev', 'CS-rev', 'CS+revearly', 'CS+revlate', 'CS-revearly', 'CS-revlate'}};


% contrast_files = {{'VITS_CS+early', 'VITS_CS+late', 'VITS_CS-early', 'VITS_CS-late', ...
%     'VITS_CS+revearly', 'VITS_CS+revlate', 'VITS_CS-revearly', 'VITS_CS-revlate'}};

% contrast_files = {{'Cond_CSplus_mean_early', 'Cond_CSplus_mean_late', 'Cond_Csminus_mean_early', 'Cond_Csminus_mean_late'},...
%     {'REV_New_CSplus_mean_early', 'REV_New_CSplus_mean_late', 'REV_New_CSminus_mean_early', 'REV_New_CSminus_mean_late'},...
%     {'Cond_CSplus_mean_early', 'Cond_CSplus_mean_late', 'Cond_Csminus_mean_early', 'Cond_Csminus_mean_late', ...
%     'REV_New_CSplus_mean_early', 'REV_New_CSplus_mean_late', 'REV_New_CSminus_mean_early', 'REV_New_CSminus_mean_late'},...
%     {'Cond_CSplus_mean', 'Cond_Csminus_mean', 'Cond_CSplus_mean_early', 'Cond_CSplus_mean_late', 'Cond_Csminus_mean_early', 'Cond_Csminus_mean_late'},...
%     {'REV_New_CSplus_mean', 'REV_New_CSminus_mean', 'REV_New_CSplus_mean_early', 'REV_New_CSplus_mean_late', 'REV_New_CSminus_mean_early', 'REV_New_CSminus_mean_late'},...
%     {'Cond_CSplus_mean', 'Cond_Csminus_mean', 'Cond_CSplus_mean_early', 'Cond_CSplus_mean_late', 'Cond_Csminus_mean_early', 'Cond_Csminus_mean_late', ...
%     'REV_New_CSplus_mean', 'REV_New_CSminus_mean', 'REV_New_CSplus_mean_early', 'REV_New_CSplus_mean_late', 'REV_New_CSminus_mean_early', 'REV_New_CSminus_mean_late'}};

contrast_names = {'early_late_cond', 'early_late_rev', 'early_late_all', ...
    'early_late_cond_all', 'early_late_rev_all', 'early_late_all_all'};

% contrast_names = {'early_late_all'};
% contrast_names = {'early_late_cond_all', 'early_late_rev_all', 'early_late_all_all'};
%% 1. Training (100%)
% int_vars = {'DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'STAI_T_A', 'SCSR_P_A', 'PCA'}; %, 'EMA_2weeks_first'
% int_var_names = {'DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'STAI_T_A', 'SCSR_P_A', 'without_EMA'};
% int_vars = {'ASI_AxTA', 'DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'PSWQ_T_A', 'IoUS_T_A', ...
%     'LSAS_T_A', 'TAG_T_A', 'STAI_T_A', 'SCSR_P_A', 'PCA_1', 'PCA_2', 'PCA_3_1', 'PCA_3_2'}; %, 'EMA_2weeks_first'
int_vars = {'IoUS_T_A', ...
    'LSAS_T_A', 'TAG_T_A', 'STAI_T_A', 'SCSR_P_A', 'PCA_1', 'PCA_2', 'PCA_3_1', 'PCA_3_2'};
% int_var_names = {'ASI_AxTA', 'DASS_A_A', 'DASS_D_A', 'DASS_S_A', 'PSWQ_T_A', 'IoUS_T_A', ...
%     'LSAS_T_A', 'TAG_T_A', 'STAI_T_A', 'SCSR_P_A', 'without_EMA', 'PCA_F1', 'PCA_F1', 'PCA_F1'};
int_var_names = {'IoUS_T_A', ...
    'LSAS_T_A', 'TAG_T_A', 'STAI_T_A', 'SCSR_P_A', 'without_EMA', 'PCA_F1', 'PCA_F1', 'PCA_F1'};
% int_vars = {'pca_all_tertil', 'pca_without_EMA_tertil', 'pca_only_DASSA_STAI_SCSRP_tertil'};
% int_var_names = {'all', 'without_EMA', 'only_DASSA_STAI_SCSRP'};

int_vars = {'SCSR_P_A'};
int_var_names = {'SCSR_P_A'};
contrast_names = {'feature_selection'};
contrast_files = {{'CS+late', 'CS-revlate'}}; %'CS+early', 'CS+late', 'CS-revlate','CS-early'

for i = 1:length(int_vars)
    int_var = int_vars{i};
    int_var_name = int_var_names{i};
    
    % data_excel = readtable(fullfile(infodir, [int_var '_SCR.xlsx']),'VariableNamingRule','preserve');
    data_excel = readtable(fullfile(infodir, [int_var '_patexp.xlsx']),'VariableNamingRule','preserve');
    data_excel.Properties.RowNames = data_excel.(data_excel.Properties.VariableNames{1});
    data_excel(:, data_excel.Properties.VariableNames{1}) = [];
    validSubjects_var = data_excel.Properties.RowNames;
    
    figure;
    histogram(data_excel.(int_var_name), 20);
    title(['Data set distribution (N = ' num2str(length(data_excel.(int_var_name))) ')']);
    xlabel([replace(int_var,'_', ' ') ' value']);
    ylabel('Frequency');
    set(gca, 'FontSize', 14)
    x0=500; y0=500; width=600; height=400;
    set(gcf,'position', [x0, y0, width, height])
    saveas(gcf, fullfile(savedir, ['Dist_' int_var '.png']))
    close;

    % 2. Developing classifiers
    roc_res = array2table(zeros(length(contrast_files), 9), 'RowNames', contrast_names, 'VariableNames', ...
        {'Accuracy', 'P', 'P_se', 'Sensitivity', 'CI_i_sens', 'CI_s_sens', 'Specificity', 'CI_i_spec', 'CI_s_spec'});

    for c = 1:length(contrast_files)
    
        % Leave-one-subject-out cross-validation
        subject_id = 1:length(data_excel.(int_var_name));
        data = fmri_data;
        data.dat = table2array(data_excel(:,contrast_files{c}))';
        data.Y = data_excel.IQ;
        [~, stats_CV] = predict(data, 'algorithm_name', 'cv_svm', 'nfolds', subject_id, 'error_type', 'mcr', 'dist_from_hyperplane_xval'); 
        % mcr: misclassiication rate 'dist_from_hyperplane_xval
        % [~, stats_boot] = predict(data, 'algorithm_name', 'cv_svm', 'nfolds', 1, 'error_type', 'mcr', 'bootweights', 'bootsamples', 5000, 'useparallel', 1);

        figure;
        ROC_CV = roc_plot(stats_CV.dist_from_hyperplane_xval, data.Y == 1, 'threshold', 0);
        x0=10; y0=10; width=900; height=800;
        set(gcf,'position', [x0, y0, width, height])
        title(['ROC curve ' replace(int_var,'_', ' ') ' ' replace(contrast_names{c},'_', ' ')])
        saveas(gcf, fullfile(savedir, ['ROC_' int_var '_' contrast_names{c} '.png']))
        close;
        
        roc_res.Accuracy(contrast_names{c}) = ROC_CV.accuracy;
        roc_res.P(contrast_names{c}) = ROC_CV.accuracy_p;
        roc_res.P_se(contrast_names{c}) = ROC_CV.accuracy_se;
        roc_res.Sensitivity(contrast_names{c}) = ROC_CV.sensitivity;
        roc_res.CI_i_sens(contrast_names{c}) = ROC_CV.sensitivity_ci(1);
        roc_res.CI_s_sens(contrast_names{c}) = ROC_CV.sensitivity_ci(2);
        roc_res.Specificity(contrast_names{c}) = ROC_CV.specificity;
        roc_res.CI_i_spec(contrast_names{c}) = ROC_CV.specificity_ci(1);
        roc_res.CI_s_spec(contrast_names{c}) = ROC_CV.specificity_ci(2);
        save(fullfile(savedir, ['workspace_' int_var '_' contrast_names{c} '.mat']));
    end
    
    writetable(roc_res, fullfile(savedir, ['ROC_' int_var '.xlsx']), "WriteRowNames",true)

end
%%
boots_threshold = threshold(stats_boot.weight_obj, .05, 'fdr');
clear; clc;
