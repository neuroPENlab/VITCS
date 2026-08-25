%% fig04_existing_signatures_accuracy.m
% -------------------------------------------------------------------
% ........
%
% Requires s09_comparison_existing_signatures.m to have been run first.
%
% Dependencies:
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as s01_train_test_split.m
savedir = fullfile(basedir, 'results', 'comparison_existing_signatures');
figdir  = fullfile(basedir, 'figures');
if ~exist(figdir, 'dir'); mkdir(figdir); end

res_accuracy = readtable(fullfile(savedir, 'accuracy_all_signatures.csv'), ...
    'ReadRowNames', true, 'VariableNamingRule', 'preserve');

%% Define colors and make plot
colors = [
    0.23 0.43 0.68;   % VTCS
    0.28 0.46 0.72;   % reddan
    0.30 0.50 0.75;   % suitas
    0.35 0.55 0.78;   % zhou
    0.40 0.60 0.80;   % wen
    0.29 0.62 0.64;   % NPS
    0.35 0.65 0.45;   % ceko general
    0.30 0.60 0.40;   % ceko mechanical
    0.40 0.70 0.50;   % ceko thermal
    0.45 0.72 0.55;   % ceko sound
    0.38 0.68 0.48;   % ceko visual
    0.80 0.45 0.55;   % craving
];

res_accuracy.acc = res_accuracy.acc*100; % convert to percentage
res_accuracy.acc_se = res_accuracy.acc_se*100; % convert to percentage

figure('Position', [400 300 1000 700]); hold on
b = bar(res_accuracy.acc, 'FaceColor', 'flat');
b.CData = colors;
er = errorbar(1:numel(res_accuracy.acc), res_accuracy.acc, res_accuracy.acc_se, ...
              'k', 'LineStyle', 'none', 'LineWidth', 1.5);
xticks(1:numel(res_accuracy.Properties.RowNames))
xticklabels(strrep(res_accuracy.Properties.RowNames, '_', ' '))
xtickangle(45)
xlabel('VITCS and previously published affective brain signatures')
set(gca, 'FontSize', 18, 'Box', 'off')
ylabel('Classification accuracy (%)', 'FontSize', 20)
ylim([35 100])
yline(50, '--', 'Chance', 'LineWidth', 1)
for i = 1:height(res_accuracy)
    text(i, res_accuracy.acc(i) + res_accuracy.acc_se(i) + 1.8, ...
        sprintf('%.0f', res_accuracy.acc(i)), ...
        'HorizontalAlignment', 'center', ...
        'FontSize', 16)
end
dif_sig = [[1, 2]; [2, 3]; [2, 4]; [2, 6]; [2, 7]; [3, 4]; [3, 5]; [3, 7]; [4, 5]; ...
    [6, 7]; [7, 8]; [9, 10]; [11, 12]; [8,9]; [10,11]; [10,12]];
for j = 1:length(dif_sig)
    y_max = max(res_accuracy.acc(dif_sig(j,:)) + res_accuracy.acc_se(dif_sig(j,:)));
    y_start = y_max + 3.8;
    if j == 3 || j == 7 || j == 15 || j == 14, y_start = y_start + 2.8; end
    if j == 4, y_start = y_start + 4.8; end
    if j == 5 || j == 8 || j == 16, y_start = y_start + 8.8; end
    % sig line
    plot([dif_sig(j,1) dif_sig(j,2)], [y_start y_start], 'k', 'LineWidth', 1.5)
    if j == 3 || j == 5 || j == 12 || j == 13
        text(mean(dif_sig(j,:)), y_start + 0.3, '*', 'HorizontalAlignment', 'center', 'FontSize', 18)
    elseif j == 1 || j == 7
        text(mean(dif_sig(j,:)), y_start + 0.3, '***', 'HorizontalAlignment', 'center', 'FontSize', 18)
    else
        text(mean(dif_sig(j,:)), y_start + 0.9, 'ns', 'HorizontalAlignment', 'center', 'FontSize', 13)
    end
end