%% s07_mediation_analysis.m
clear; clc;
% Mediation analysis
basedir = '/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask'; 
% pat_exp = readtable(fullfile(basedir, '3_sig_evaluation_test/results_new_CS+CS-diff/all_pat_exp_new.xlsx'), 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
% pat_exp = readtable(fullfile(basedir, '2_SVM_results_stai_neurosynth/VALIDATION/_Pattern_expression_allsample.xlsx'), 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
% pat_exp = readtable(fullfile(basedir, '2_SVM_results_stai/pat_exp_all_data_xval.xlsx'), 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
pat_exp = readtable(fullfile(basedir, '2_SVM_results_stai/pat_exp_all_data_xval_10fold.xlsx'), 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
% pat_exp = readtable(fullfile(basedir, '1_sig_evaluation/pat_exp_suitas.xlsx'), 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
skin = readtable(fullfile(basedir, 'SKIN_ARO_VAL', 'SCR_detrend.xlsx'), 'ReadRowNames', true);
subj_rat = readtable(fullfile(basedir, 'SKIN_ARO_VAL', 'Subjective_ratings_condrev.xlsx'), 'ReadRowNames', true);

pat_exp.Properties.RowNames = erase(pat_exp.Properties.RowNames, "sub-");
pat_exp.Properties.VariableNames = strcat("VITS_", pat_exp.Properties.VariableNames);
cols_to_keep1 = {'VITS_CS+', 'VITS_CS-', 'VITS_CS+early', 'VITS_CS+late', 'VITS_CS-early', 'VITS_CS-late', ...
    'VITS_CS+rev', 'VITS_CS-rev', 'VITS_CS+revearly', 'VITS_CS+revlate', 'VITS_CS-revearly', 'VITS_CS-revlate'};
% cols_to_keep1 = {'suitas_CS+', 'suitas_CS-', 'suitas_CS+early', 'suitas_CS+late', 'suitas_CS-early', 'suitas_CS-late', ...
%     'suitas_CS+rev', 'suitas_CS-rev', 'suitas_CS+revearly', 'suitas_CS+revlate', 'suitas_CS-revearly', 'suitas_CS-revlate'};
% cols_to_keep1 = {'reddan_CS+', 'reddan_CS-', 'reddan_CS+early', 'reddan_CS+late', 'reddan_CS-early', 'reddan_CS-late', ...
%     'reddan_CS+rev', 'reddan_CS-rev', 'reddan_CS+revearly', 'reddan_CS+revlate', 'reddan_CS-revearly', 'reddan_CS-revlate'};
pat_exp_sub = pat_exp(:, cols_to_keep1);

cols_to_keep2 = {'Cond_CSplus_mean', 'Cond_Csminus_mean', 'Cond_CSplus_mean_early', 'Cond_CSplus_mean_late', 'Cond_Csminus_mean_early', 'Cond_Csminus_mean_late', ...
    'REV_New_CSplus_mean', 'REV_New_CSminus_mean', 'REV_New_CSplus_mean_early', 'REV_New_CSplus_mean_late', 'REV_New_CSminus_mean_early', 'REV_New_CSminus_mean_late'};
skin_sub = skin(:, cols_to_keep2);
skin_sub.Properties.VariableNames = cols_to_keep1;

cols_to_keep3 = {'COND_CSplus_VAL', 'COND_CSplus_ARO', 'COND_CSminus_VAL', 'COND_Csminus_ARO', ...
    'REV_New_Csplus_VAL', 'REV_New_CSplus_ARO', 'REV_New_CSminus_VAL', 'REV_New_CSminus_ARO'};
subj_rat_sub = subj_rat(:, cols_to_keep3);

common_idx = intersect(intersect(pat_exp.Properties.RowNames, skin.Properties.RowNames), subj_rat.Properties.RowNames);
common_idx2 = intersect(pat_exp.Properties.RowNames, subj_rat.Properties.RowNames);

pat_exp_subset = pat_exp_sub(common_idx, :);
skin_subset = skin_sub(common_idx, :);
subj_rat_subset = subj_rat_sub(common_idx, :);

pat_exp_subset = pat_exp_sub(common_idx2, :);
subj_rat_subset = subj_rat_sub(common_idx2, :);
newRows = array2table(ones(length(setdiff(common_idx2, common_idx, 'stable')), width(skin_sub)), ...
    'VariableNames', skin_sub.Properties.VariableNames);
newRows.Properties.RowNames = setdiff(common_idx2, common_idx, 'stable');
skin_subset = [skin_sub; newRows];
skin_subset = skin_subset(pat_exp_subset.Properties.RowNames, :);

X = zscore(pat_exp_subset.("VITS_CS+")); % VITS_CS+rev
X = pat_exp_subset.("VITS_CS+") - pat_exp_subset.("VITS_CS-"); % VITS_CS+rev
% X = pat_exp_subset.("suitas_CS+") - pat_exp_subset.("suitas_CS-"); % suitas_CS+rev

% Y = subj_rat_subset.COND_CSplus_ARO; % COND_CSplus_ARO REV_New_CSplus_ARO
% Y = subj_rat_subset.COND_CSplus_ARO - subj_rat_subset.COND_Csminus_ARO; % COND_CSplus_ARO REV_New_CSplus_ARO
Y = (subj_rat_subset.COND_CSplus_VAL - 6)*-1; % COND_CSplus_VAL REV_New_Csplus_VAL
% Y = (subj_rat_subset.COND_CSplus_VAL - 6)*-1 - (subj_rat_subset.COND_CSminus_VAL - 6)*-1; % COND_CSplus_VAL REV_New_Csplus_VAL

M = skin_subset.("VITS_CS+");  % VITS_CS+rev
M = skin_subset.("VITS_CS+") - skin_subset.("VITS_CS-");  % VITS_CS+rev
% M = skin_subset.("suitas_CS+") - skin_subset.("suitas_CS-");  % suitas_CS+rev

% [paths, stats2] = mediation(X, Y, M, 'plots', 'verbose', 'doCIs');
[paths, stats3] = mediation(X, Y, M, 'plots', 'boot', 'bootsamples', 10000, 'verbose', 'doCIs'); %, 'plots'

[r,p] = corr(X, Y)
[r,p] = corr(X, M)

%% Bootstrapp to compare VITCS vs SUITAS

% path c: Y = cX + E
% In each interation, we calculate c for both and we save the difference
% We have 10000 differences
% Calculate statistical inference (is this difference significantly
% different from 0?) --> prctile [2.5, 97.5] --> 2,5 x 2 = 5 -> 95% conf

vitcs = readtable(fullfile(basedir, '2_SVM_results_stai/pat_exp_all_data_xval.xlsx'), 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
suitas = readtable(fullfile(basedir, '1_sig_evaluation/pat_exp_SUITAS.xlsx'), 'ReadRowNames', true, 'VariableNamingRule', 'preserve');

X_vitcs = zscore(vitcs.("CS+"));
X_suitas = zscore(suitas.("suitas_CS+"));
Y = zscore(subj_rat_subset.COND_CSplus_ARO);
% Y = zscore((subj_rat_subset.COND_CSplus_VAL - 6)*-1);

nBoot = 10000;
N = length(Y);

delta_c = nan(nBoot,1);

for b = 1:nBoot
    idx = randsample(N, N, true);

    Xv = X_vitcs(idx);
    Xs = X_suitas(idx);
    Yb = Y(idx);

    c_v = regress(Yb, [ones(N,1) Xv]);
    c_s = regress(Yb, [ones(N,1) Xs]);

    delta_c(b) = c_v(2) - c_s(2);
end

CI = prctile(delta_c, [2.5 97.5]);
p = mean(abs(delta_c) >= abs(mean(delta_c)));  % opcional


corr(X_suitas, Y)
corr(X_vitcs, Y)

%% calculate direct correlations! VITS - Subj.Ratings (més sample)
common_idx2 = intersect(pat_exp.Properties.RowNames, subj_rat.Properties.RowNames);
pat_exp_subset2 = pat_exp_sub(common_idx2, :);
subj_rat_subset2 = subj_rat_sub(common_idx2, :);

% X2 = pat_exp_subset2.("VITS_CS+"); % VITS_CS+rev
X2 = pat_exp_subset2.("suitas_CS+"); % suitas_CS+rev
% Y2 = subj_rat_subset2.COND_CSplus_ARO; % COND_CSplus_ARO REV_New_CSplus_ARO
Y2 = (subj_rat_subset2.COND_CSplus_VAL - 6)*-1; % COND_CSplus_VAL REV_New_Csplus_VAL

% [RHO,PVAL] = corr(pat_exp_subset2.("VITS_CS+"), subj_rat_subset2.COND_CSplus_ARO)
 % 'bootsamples', 10000

% Regression
fprintf('\nREGRESSION\n')

% [betaXY2, statsXY2] = robustfit(X2, Y2);
% fprintf('\nRelation X2-Y2:\nCoeff = %.5f\nSTE = %.5f\nt = %.5f\np = %.5f\n', ...
%     betaXY2(2), statsXY2.se(2), statsXY2.t(2), statsXY2.p(2));
x2=[ones(size(X2)) X2];
[betaXY2, ~, residuals, ~, statsXY2] = regress(Y2,x2);
XtX_inv = inv(x2' * x2);
STE = sqrt(statsXY2(4) * XtX_inv(2,2));
t = betaXY2(2) / STE;
fprintf('\nRelation X2-Y2 (regress):\nCoeff = %.5f\nSTE = %.5f\nt = %.3f\np = %.5f\n', ...
    betaXY2(2), STE, t, statsXY2(3));

% comprovació!
% [betaXY, statsXY] = robustfit(X, Y);
% fprintf('\nRelation X-Y:\nCoeff = %.5f\nSTE = %.5f\nt = %.5f\np = %.5f\n', ...
%     betaXY(2), statsXY.se(2), statsXY.t(2), statsXY.p(2));
x=[ones(size(X)) X];
[betaXY, ~, residuals, ~, statsXY] = regress(Y,x);
XtX_inv = inv(x' * x);
STE = sqrt(statsXY(4) * XtX_inv(2,2));
t = betaXY(2) / STE;
fprintf('\nRelation X-Y (regress):\nCoeff = %.5f\nSTE = %.5f\nt = %.3f\np = %.5f\n', ...
    betaXY(2), STE, t, statsXY(3));


% [betaXM, statsXM] = robustfit(X, M);
% fprintf('\nRelation X-M:\nCoeff = %.5f\nSTE = %.5f\nt = %.5f\np = %.5f\n', ...
%     betaXM(2), statsXM.se(2), statsXM.t(2), statsXM.p(2));
[betaXM, ~, residuals, ~, statsXM] = regress(M,x);
STE = sqrt(statsXM(4) * XtX_inv(2,2));
t = betaXM(2) / STE;
fprintf('\nRelation X-M (regress):\nCoeff = %.5f\nSTE = %.5f\nt = %.3f\np = %.5f\n', ...
    betaXM(2), STE, t, statsXM(3));


% --- Bootstrap del coeficient ---
nBoot = 1000;
n = length(Y2);
B = zeros(nBoot,1);
for i = 1:nBoot
    idx = randsample(n, n, true);
    Xb = [ones(n,1) X2(idx)];
    Yb = Y2(idx);
    b = regress(Yb, Xb);
    B(i) = b(2);
end

beta_obs = betaXY2(2);
beta_boot_mean = mean(B);
se_boot = std(B);
ci_boot = prctile(B, [2.5 97.5]);
z = beta_obs / se_boot;
p_norm_approx = 2 * (1 - 0.5*(1+erf(abs(z)/sqrt(2))));  % equivalent normcdf

fprintf('\nBootstrap (%d it):\nCoeff(mean) = %.5f\nSTE(boot) = %.5f\nIC95%% = [%.5f, %.5f]\n', ...
    nBoot, beta_boot_mean, se_boot, ci_boot(1), ci_boot(2));
fprintf('p (normal approx) = %.5f\n', p_norm_approx);

% --- Permutation test (no paramètric) ---
nPerm = 5000;
beta_perm = zeros(nPerm,1);
for i = 1:nPerm
    idx = randperm(n);    % permutació sense reemplaçament (H0)
    Yp = Y2(idx);
    b = regress(Yp, x2);
    beta_perm(i) = b(2);
end
p_perm = mean(abs(beta_perm) >= abs(beta_obs));
fprintf('p (permutation, %d perm) = %.5f\n', nPerm, p_perm);




% beta(2)     = coeff
% stats.se(2) = Standard error
% stats.t(2)  = t-statistic
% stats.p(2)  = p-value

% Correlation
% fprintf('\nCORRELATION\n')
% 
% [RHOXY2,PVALXY2] = corr(X2, Y2);
% fprintf('\nRelation X2-Y2:\nCoeff = %.5f\np = %.5f\n', ...
%     RHOXY2, PVALXY2);
% 
% % comprovació!
% [RHOXY,PVALXY] = corr(X, Y);
% fprintf('\nRelation X-Y:\nCoeff = %.5f\np = %.5f\n', ...
%     RHOXY, PVALXY);
% 
% [RHOXM,PVALXM] = corr(X, M);
% fprintf('\nRelation X-M:\nCoeff = %.5f\np = %.5f\n', ...
%     RHOXM, PVALXM);
