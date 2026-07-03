clear; clc;
basedir = '.';
save_results = fullfile(basedir, 'results', 'final_brainmask', '5_multiple_regression', 'results_matlab');
sig_names = {'Our_sig', 'Threat', 'SUITAS'};

data_var = readtable(fullfile(basedir, 'MVPA_dataset_new.xlsx'));
data_var(174,:) = [];
data_var(173,:) = [];
contdirs = dir(fullfile(basedir, 'contrasts_brainmask'));
subj_names = {contdirs([contdirs.isdir]).name};
subj_names = subj_names(~ismember(subj_names, {'.', '..'}))';

res_tot = array2table(zeros(48, 3), 'VariableNames', {'Ncoeff', 'R2', 'R2adj'}); % , 'formula'

cli_var = data_var;
for var = {'STAI_T_A', 'SCSR_P_A', 'SCSR_R_A', 'IoUS_T_A', 'EMA_2weeks_first', 'DASS_S_pre', 'DASS_D_pre', 'DASS_A_pre'}

    res = array2table(zeros(4, 3), 'VariableNames', {'Ncoeff', 'R2', 'R2adj'}); % , 'formula'
    res.Properties.RowNames = {'cond_linear', 'cond_interactions', 'cond_rev_linear', 'cond_rev_interactions'};

    % Check subjects that have both fMRI and clinical data
    list_subj = cellfun(@(str) ['sub-' str], cli_var.ID, 'UniformOutput', false);
    cli_var.Properties.RowNames = list_subj;
    list_subj_var = list_subj(~isnan(cli_var.(var{1})));
    validSubjects_var = ismember(list_subj_var, subj_names);
    cli_var = cli_var(validSubjects_var, :);
    
    % Upload pattern expression values extracted previously
    pat_exp_cond = readtable(fullfile(basedir, 'results', 'final_brainmask', '5_multiple_regression', 'cond_rev_pat_exp_Zscores.xlsx'),'VariableNamingRule','preserve');
    validSubjects_pat = ismember(subj_names, list_subj_var);
    pat_exp_cond = pat_exp_cond(validSubjects_pat, :);
    Y = cli_var.(var{1});

    tbl = pat_exp_cond(:, [2:7,14:16]);
    tbl.(var{1}) = Y;
    ini_mdl1 = fitlm(tbl);
    mdl11 = stepwiselm(rmmissing(tbl), 'linear', 'ResponseVar', var{1});
    res{'cond_linear', 'Ncoeff'} = mdl11.NumCoefficients;
    res{'cond_linear', 'R2'} = mdl11.Rsquared.Ordinary;
    res{'cond_linear', 'R2adj'} = mdl11.Rsquared.Adjusted;
    res_tot{['cond_linear' var{1}], 'Ncoeff'} = mdl11.NumCoefficients;
    res_tot{['cond_linear' var{1}], 'R2'} = mdl11.Rsquared.Ordinary;
    res_tot{['cond_linear' var{1}], 'R2adj'} = mdl11.Rsquared.Adjusted;
    try
        res{'cond_linear', 'formula'} = mdl11.Formula.LinearPredictor;
        res_tot{['cond_linear' var{1}], 'formula'} = mdl11.Formula.LinearPredictor;
    end
    mdl12 = stepwiselm(rmmissing(tbl), 'interactions', 'ResponseVar', var{1});
    res{'cond_interactions', 'Ncoeff'} = mdl12.NumCoefficients;
    res{'cond_interactions', 'R2'} = mdl12.Rsquared.Ordinary;
    res{'cond_interactions', 'R2adj'} = mdl12.Rsquared.Adjusted;
    res_tot{['cond_interactions' var{1}], 'Ncoeff'} = mdl12.NumCoefficients;
    res_tot{['cond_interactions' var{1}], 'R2'} = mdl12.Rsquared.Ordinary;
    res_tot{['cond_interactions' var{1}], 'R2adj'} = mdl12.Rsquared.Adjusted;
    try
        res{'cond_interactions', 'formula'} = mdl12.Formula.LinearPredictor;
        res_tot{['cond_interactions' var{1}], 'formula'} = mdl12.Formula.LinearPredictor;
    end

    tbl2 = pat_exp_cond(:, 2:19);
    tbl2.(var{1}) = Y;
    ini_mdl2 = fitlm(tbl2);
    mdl21 = stepwiselm(rmmissing(tbl2), 'linear', 'ResponseVar', var{1});
    res{'cond_rev_linear', 'Ncoeff'} = mdl21.NumCoefficients;
    res{'cond_rev_linear', 'R2'} = mdl21.Rsquared.Ordinary;
    res{'cond_rev_linear', 'R2adj'} = mdl21.Rsquared.Adjusted;
    res_tot{['cond_rev_linear' var{1}], 'Ncoeff'} = mdl21.NumCoefficients;
    res_tot{['cond_rev_linear' var{1}], 'R2'} = mdl21.Rsquared.Ordinary;
    res_tot{['cond_rev_linear' var{1}], 'R2adj'} = mdl21.Rsquared.Adjusted;
    try
        res{'cond_rev_linear', 'formula'} = mdl21.Formula.LinearPredictor;
        res_tot{['cond_rev_linear' var{1}], 'formula'} = mdl21.Formula.LinearPredictor;
    end
    mdl22 = stepwiselm(rmmissing(tbl2), 'interactions','ResponseVar', var{1});
    res{'cond_rev_interactions', 'Ncoeff'} = mdl22.NumCoefficients;
    res{'cond_rev_interactions', 'R2'} = mdl22.Rsquared.Ordinary;
    res{'cond_rev_interactions', 'R2adj'} = mdl22.Rsquared.Adjusted;
    res_tot{['cond_rev_interactions' var{1}], 'Ncoeff'} = mdl22.NumCoefficients;
    res_tot{['cond_rev_interactions' var{1}], 'R2'} = mdl22.Rsquared.Ordinary;
    res_tot{['cond_rev_interactions' var{1}], 'R2adj'} = mdl22.Rsquared.Adjusted;
    try
        res{'cond_rev_interactions', 'formula'} = mdl22.Formula.LinearPredictor;
        res_tot{['cond_rev_interactions' var{1}], 'formula'} = mdl22.Formula.LinearPredictor;
    end
    writetable(res, fullfile(save_results, ['mult_reg_sw_' var{1} '.xlsx']), 'WriteRowNames', true);

    figure;
    subplot(2,2,1);
    plotResiduals(mdl11);
    title('cond linear')
    subplot(2,2,2);
    plotResiduals(mdl12);
    title('cond interactions')
    subplot(2,2,3);
    plotResiduals(mdl21);
    title('cond rev linear')
    subplot(2,2,4);
    plotResiduals(mdl22);
    title('cond rev interactions')
    x0=400; y0=400; width=1500; height=900;
    set(gcf,'position', [x0, y0, width, height])
    allAx = findall(gcf, 'Type', 'axes');
    linkaxes(allAx, 'xy');
    saveas(gcf, fullfile(save_results, ['mult_reg_sw_' var{1} '.png']))
end

h=heatmap(res_tot{:,2:3});
colormap("hot");
h.XDisplayLabels = {'R2', 'R2adj'};
h.YDisplayLabels = cellfun(@(x) strrep(x, '_', ' '), res_tot.Properties.RowNames, 'UniformOutput', false);

writetable(res_tot, fullfile(save_results, 'mult_reg_sw.xlsx'), 'WriteRowNames', true);