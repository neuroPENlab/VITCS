%% fig02b_test_set_roc_plot.m
% -------------------------------------------------------------------
% Plot the three ROC curves (Training set 10-fold CV, Test set
% Acquisition, Test set Reversal) together, as in the manuscript
% figure.
%
% Requires s03_1_validation_VITCS_test_set.m to have been run first.
%
% Dependencies: CANlab Core Tools (roc_plot)
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
% Pastel colors
col1 = [239,  83,  80] / 255;  % coral (Training set, CV)
col2 = [ 63,  81, 181] / 255;  % indigo (Test set, Acquisition)
col3 = [ 38, 166, 154] / 255;  % teal (Test set, Reversal)

figure;
r1 = roc_plot(R.CV_roc_inputs.xval_dist_C1, R.CV_roc_inputs.outcome_C1, ...
    'threshold', 'pairedobservations', 'color', col1);
hold on;
r2 = roc_plot(R.pat_exp_acq, R.outcome_acq, 'threshold', 'pairedobservations', 'color', col2);
hold on;
r3 = roc_plot(R.pat_exp_rev, R.outcome_rev, 'threshold', 'pairedobservations', 'color', col3);
hold off;

r1.line_handle(2).LineWidth = 3;
r2.line_handle(2).LineWidth = 3;
r3.line_handle(2).LineWidth = 3;

title('ROC plot', 'FontSize', 30);
lgd = legend([r1.line_handle(2), r2.line_handle(2), r3.line_handle(2)], ...
    {'CV - Training set', 'Acquisition Test set', 'Reversal Test set'}, ...
    'Location', 'southeast');
lgd.FontSize = 21;
set(gca, 'FontSize', 28);
x0 = 10; y0 = 10; width = 500; height = 450;
set(gcf, 'position', [x0, y0, width, height]);

saveas(gcf, fullfile(figdir, 'fig02b_ROC_test_set_and_CV.png'));