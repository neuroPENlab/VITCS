% Script to correlate brain pattern expressions with clinical variables
clear; clc;
basedir = '.';
save_results = fullfile(basedir, 'results', 'final_brainmask', '4_correlations_good');
sig_names = {'Our_sig', 'Threat', 'SUITAS', 'PINES', 'VIFS'};

data_var = readtable(fullfile(basedir, 'MVPA_dataset_new.xlsx'));
data_var(174,:) = [];
data_var(173,:) = [];
contdirs = dir(fullfile(basedir, 'contrasts_brainmask'));
subj_names = {contdirs([contdirs.isdir]).name};
subj_names = subj_names(~ismember(subj_names, {'.', '..'}))';

for data_ana = {'all', 'Woman', 'Man'}
    if strcmp(data_ana{1}, 'all')
        cli_var = data_var;
    else
        cli_var = data_var(strcmp(data_var.Sex, data_ana{1}), :);
    end
    % Check subjects that have both fMRI and clinical data
    list_subj = cellfun(@(str) ['sub-' str], cli_var.ID, 'UniformOutput', false);
    cli_var.Properties.RowNames = list_subj;
    validSubjects_var = ismember(list_subj, subj_names);
    cli_var = cli_var(validSubjects_var, :);

    name_cli_vars = cli_var.Properties.VariableNames(6:15); %end 15
    
    % Upload pattern expression values extracted previously
    pat_exp_cond = readtable(fullfile(save_results, 'all_cond_pat_exp.xlsx'),'VariableNamingRule','preserve');
    pat_exp_rev = readtable(fullfile(save_results, 'all_rev_pat_exp.xlsx'),'VariableNamingRule','preserve');
    validSubjects_pat = ismember(subj_names, list_subj);
    pat_exp_cond = pat_exp_cond(validSubjects_pat, :);
    pat_exp_rev = pat_exp_rev(validSubjects_pat, :);
    
    corr_R = table();
    corr_P = table();
    for sig = sig_names
        % Conditioning
        for cont = {'CS+', 'CS-', 'CS+early', 'CS+late', 'CS-early', 'CS-late'}
            for var = name_cli_vars
                if iscell(cli_var{:, var{1}})
                    in_data = [pat_exp_cond{:, [sig{1} '_' cont{1}]}, str2double(cli_var{:, var{1}})];
                    [R, P] = corrcoef(rmmissing(in_data));
                else
                    in_data = [pat_exp_cond{:, [sig{1} '_' cont{1}]}, cli_var{:, var{1}}];
                    [R, P] = corrcoef(rmmissing(in_data));
                end
                corr_R{[sig{1} '_' cont{1}], var{1}} = R(1,2);
                corr_P{[sig{1} '_' cont{1}], var{1}} = P(1,2);
            end
        end
        % Reversal
        for cont = {'CS+rev', 'CS-rev'}
            for var = name_cli_vars
                if iscell(cli_var{:, var{1}})
                    in_data = [pat_exp_rev{:, [sig{1} '_' cont{1}]}, str2double(cli_var{:, var{1}})];
                    [R, P] = corrcoef(rmmissing(in_data));
                else
                    in_data = [pat_exp_rev{:, [sig{1} '_' cont{1}]}, cli_var{:, var{1}}];
                    [R, P] = corrcoef(rmmissing(in_data));
                end
                corr_R{[sig{1} '_' cont{1}], var{1}} = R(1,2);
                corr_P{[sig{1} '_' cont{1}], var{1}} = P(1,2);
            end
        end
    end
    writetable(corr_R, fullfile(save_results, ['correlations_R_' data_ana{1} '.xlsx']), 'WriteRowNames', true);
    writetable(corr_P, fullfile(save_results, ['correlations_P_' data_ana{1} '.xlsx']), 'WriteRowNames', true);
    
    % Visualize with heatmap
    % Correlation coefficient
    h = heatmap(table2array(corr_R));
    colormap('jet'); % parula
    h.XDisplayLabels = cellfun(@(x) strrep(x, '_', ' '), corr_R.Properties.VariableNames, 'UniformOutput', false);
    h.YDisplayLabels = cellfun(@(x) strrep(x, '_', ' '), corr_R.Properties.RowNames, 'UniformOutput', false);
    h.XLabel = 'Clinical variable';
    h.YLabel = 'Signature - contrast';
    h.Title = 'Correlation coefficients';
    x0=10; y0=10; width=1000; height=1100;
    set(gcf,'position', [x0, y0, width, height])
    saveas(gcf, fullfile(save_results, 'plots_corr_less_cov2', ['corr_R_' data_ana{1} '.png']))
    % clim([-1, 1]);
    % clim([-max(max(abs(table2array(corr_R)))), max(max(abs(table2array(corr_R))))]);
    
    % Correlations p-val
    h = heatmap(table2array(corr_P));
    cmap = flipud(hot);
    colormap(cmap);
    h.XDisplayLabels = cellfun(@(x) strrep(x, '_', ' '), corr_P.Properties.VariableNames, 'UniformOutput', false);
    h.YDisplayLabels = cellfun(@(x) strrep(x, '_', ' '), corr_P.Properties.RowNames, 'UniformOutput', false);
    h.XLabel = 'Clinical variable';
    h.YLabel = 'Signature - contrast';
    h.Title = 'Correlation pval';
    clim([min(min(table2array(corr_P))), 0.06]);
    x0=10; y0=10; width=1000; height=1100;
    set(gcf, 'position', [x0, y0, width, height])
    saveas(gcf, fullfile(save_results, 'plots_corr_less_cov2', ['corr_P_' data_ana{1} '.png']))
end