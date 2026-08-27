%% fig02c_test_set_barplot.m
% -------------------------------------------------------------------
% Plot pattern expression (VITCS dot product) for CS+ vs. CS- in the
% Test Set, separately for the acquisition and reversal contrasts.
%
% Requires s03_1_validation_VITCS_test_set.m to have been run first.
%
% For the VITCS-early and VITCS-late ROC plot, change the savedir to point
% to its validation_test_set_results.mat folder respectively. 
%
% Dependencies: barplot_columns_modified.m - a locally modified copy of
%               CANlab's barplot_columns.m, kept alongside the original
%               in your CANlab Core Tools installation. See
%               scripts/barplot_columns_modified_MODIFICATION.md for
%               exact, step-by-step instructions to create it yourself
%               before running this script. As long as your CANlab
%               installation is on the MATLAB path (see Installation in
%               the main README), no extra addpath call is needed here.
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
savedir = fullfile(basedir, 'results', 'VITCS_validation');   % <-- if necessary, EDIT THIS
figdir  = fullfile(basedir, 'figures');
if ~exist(figdir, 'dir'); mkdir(figdir); end

%% Load results from s03_validation_VITCS_test_set.m 
R = load(fullfile(savedir, 'validation_test_set_results.mat'));

%% Plot
titles = {'Acquisition Test set', 'Reversal Test set'};
filenames = {'fig02c_test_set_acquisition_barplot.png', 'fig02c_test_set_reversal_barplot.png'};
colors = {[.4 .6 1], [1 1 0]};

for C = 1:length(R.contrast_names)
    contrast_name = R.contrast_names{C};

    figure;
    barplot_columns_modified(R.res_pat_exp{R.subj_ts, contrast_name}, 'nofigure', ...
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