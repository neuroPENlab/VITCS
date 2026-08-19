%% fig02c_test_set_barplot.m
% -------------------------------------------------------------------
% Plot pattern expression (VITCS dot product) for CS+ vs. CS- in the
% Test Set, separately for the acquisition and reversal contrasts.
%
% Requires 03_validation_test_set.m to have been run first.
%
% Dependencies: utils/barplot_columns_angels.m (modified from CANlab's
%               barplot_columns.m - see file header for license note)
% -------------------------------------------------------------------
clear; clc;
addpath('../utils');

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
basedir = '/Users/acalvet/Repositories/neuroPENlab/VITCS';
savedir = fullfile(basedir, 'results', 'VITCS_validation');   % <-- if necessary, EDIT THIS
figdir  = fullfile(basedir, 'figures');
if ~exist(figdir, 'dir'); mkdir(figdir); end

%% Load results from s03_validation_VITCS_test_set.m 
R = load(fullfile(savedir, 'validation_test_set_results.mat'));

%% Plot
titles = {'Acquisition Test set', 'Reversal Test set'};
filenames = {'test_set_acquisition_barplot.png', 'test_set_reversal_barplot.png'};
colors = {[.4 .6 1], [1 1 0]};

for C = 1:length(R.contrast_names)
    contrast_name = R.contrast_names{C};

    figure;
    barplot_columns_angels(R.res_pat_exp{R.subj_ts, contrast_name}, 'nofigure', ...
        'colors', colors, 'names', contrast_name, 'dolines');
    set(gca, 'FontSize', 34);
    ylabel('Pattern expression');
    xlabel('');
    ylim([-3, 6.5]);
    title(titles{C});
    x0 = 10; y0 = 10; width = 800; height = 650;
    set(gcf, 'position', [x0, y0, width, height]);
    saveas(gcf, fullfile(figdir, filenames{C}));
end