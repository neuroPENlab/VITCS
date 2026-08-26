%% s07_mediation_analysis.m
% -------------------------------------------------------------------
% Test whether skin conductance responses (SCRs) mediate the
% association between brain signatures expression during threat 
% acquisition and participants' subjective ratings (arousal and 
% valence, separate models).
%
% From Methods: "First, we established a positive association between
% the independent variable (X; VITCS brain response during the CS+
% trials for each participant) and the dependent variable (Y; perceived
% arousal or valence). Once these neural-subjective associations were
% confirmed (significant path c), we examined whether they were
% mediated by SCRs [...] (mediator M) [...]. Statistical significance
% of the mediation effect and each individual path (a, b, and a*b) was
% assessed using a bias-corrected and accelerated bootstrap procedure
% [...] randomly sampling with replacement 10,000 observations."
%
% From Results: path c (total effect) is reported on the full available
% sample (N = 172, participants with both VITCS pattern expression and
% subjective ratings). Paths a, b, c', and the indirect effect (a*b)
% are reported on the smaller subsample with usable SCR data (n = 165;
% 7 participants excluded from SCR analyses due to recording
% artifacts - see Methods, "Skin conductance responses").
%
% IMPORTANT: path c is computed via a direct bootstrap regression of Y 
% on X on the full N=172 sample. Path c doesn't mathematically depend 
% on M (so the reported number was unaffected), so path c is computed 
% independently and directly instead.
%
% Run once per signature: set SIGNATURE below and re-run.
%
% Dependencies: CANlab Mediation Toolbox (mediation.m), Statistics 
% and Machine Learning Toolbox (regress, randsample)
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as previous scripts

scr_path = '<PATH_TO_SCR_DATA>';               % <-- EDIT THIS: SCR_detrend.xlsx equivalent
subj_rat_path = '<PATH_TO_SUBJECTIVE_RATINGS_DATA>'; % <-- EDIT THIS: Subjective_ratings_condrev.xlsx equivalent

%% Which signature to run mediation for
SIGNATURE = 'VITCS'; % <-- EDIT THIS: 'VITCS' | 'Reddan-Threat' | 'Liu-SUITAS' | 'VITCS_early' | 'VITCS_late'

switch SIGNATURE
    case 'VITCS'
        pat_exp_path = fullfile(basedir, 'results', 'VITCS_development', 'pat_exp_full_sample_xval.xlsx'); % from 04b + 04d
        pat_exp_col = 'CS+';
        savedir = fullfile(basedir, 'results', 'VITCS_mediation');
    case 'Reddan-Threat'
        pat_exp_path = fullfile(basedir, 'results', 'comparison_existing_signatures', 'pat_exp_full_sample_all_signatures.xlsx'); % from 04d
        pat_exp_col = 'Reddan-Threat_CS+';
        savedir = fullfile(basedir, 'results', 'comparison_existing_signatures');
    case 'Liu-SUITAS'
        pat_exp_path = fullfile(basedir, 'results', 'comparison_existing_signatures', 'pat_exp_full_sample_all_signatures.xlsx'); % from 04d
        pat_exp_col = 'Liu-SUITAS_CS+';
        savedir = fullfile(basedir, 'results', 'comparison_existing_signatures');
    case 'VITCS_early'
        pat_exp_path = fullfile(basedir, 'results', 'VITCS_early_results', 'pat_exp_full_sample_xval.xlsx'); % from 04c
        pat_exp_col = 'CS+';
        savedir = fullfile(basedir, 'results', 'VITCS_early_results');
    case 'VITCS_late'
        pat_exp_path = fullfile(basedir, 'results', 'VITCS_late_results', 'pat_exp_full_sample_xval.xlsx'); % from 04c
        pat_exp_col = 'CS+';
        savedir = fullfile(basedir, 'results', 'VITCS_late_results');
end

%% Load data
skin = readtable(scr_path, 'ReadRowNames', true);
subj_rat = readtable(subj_rat_path, 'ReadRowNames', true);

skin_sub = skin(:, 'Cond_CSplus_mean');
subj_rat_sub = subj_rat(:, {'COND_CSplus_ARO', 'COND_CSplus_VAL'});

pat_exp = readtable(pat_exp_path, 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
pat_exp.Properties.RowNames = erase(pat_exp.Properties.RowNames, "sub-");
pat_exp_sub = pat_exp(:, pat_exp_col);

%% Build the two samples: full (N=172) and SCR-available (n=165)
full_idx = intersect(pat_exp.Properties.RowNames, subj_rat.Properties.RowNames);   % pattern expression + ratings
scr_idx  = intersect(full_idx, skin.Properties.RowNames);                          % + usable SCR

fprintf('Signature: %s\n', SIGNATURE);
fprintf('Full sample (pattern expression + ratings): N = %d\n', length(full_idx));
fprintf('SCR-available subsample: n = %d\n', length(scr_idx));

pat_exp_full = pat_exp_sub(full_idx, :);
subj_rat_full = subj_rat_sub(full_idx, :);

pat_exp_scr = pat_exp_sub(scr_idx, :);
subj_rat_scr = subj_rat_sub(scr_idx, :);
skin_scr = skin_sub(scr_idx, :);

%% Define X (VITCS), M (SCR) for the mediation model
X_full = pat_exp_full.(pat_exp_col);
X_scr  = pat_exp_scr.(pat_exp_col); 
M_scr  = skin_scr.Cond_CSplus_mean; 

% Y: arousal and valence, as two separate models (valence reverse-coded
% so higher = more negative, matching "perceived negative valence").
Y_arousal_full = subj_rat_full.COND_CSplus_ARO;
Y_valence_full = (subj_rat_full.COND_CSplus_VAL - 6) * -1;

Y_arousal_scr = subj_rat_scr.COND_CSplus_ARO;
Y_valence_scr = (subj_rat_scr.COND_CSplus_VAL - 6) * -1;

%% Path c: total effect, full sample (N=172) - bootstrapped, no mediator --------
% Same inference method (bootstrap, bootsamples=10000) as the mediation()
% calls below, computed independently via a simple bootstrapped
% regression - M is never touched, no fabricated data anywhere.
nboot_pathc = 10000;
n_full = length(X_full);
x_design = [ones(n_full, 1) X_full];
 
beta_arousal = regress(Y_arousal_full, x_design);
beta_arousal = beta_arousal(2);
beta_valence = regress(Y_valence_full, x_design);
beta_valence = beta_valence(2);
 
boot_beta_arousal = nan(nboot_pathc, 1);
boot_beta_valence = nan(nboot_pathc, 1);
for b = 1:nboot_pathc
    idx = randsample(n_full, n_full, true);
    xb = [ones(n_full, 1) X_full(idx)];
 
    beta_b = regress(Y_arousal_full(idx), xb);
    boot_beta_arousal(b) = beta_b(2);
 
    beta_b = regress(Y_valence_full(idx), xb);
    boot_beta_valence(b) = beta_b(2);
end

se_arousal = std(boot_beta_arousal);
ci_arousal = prctile(boot_beta_arousal, [2.5 97.5]);
p_arousal = 2 * min(mean(boot_beta_arousal >= 0), mean(boot_beta_arousal <= 0));
t_arousal = beta_arousal / se_arousal;   % pseudo-t: point estimate / bootstrap SE
fprintf('\nPath c (arousal, N=%d, bootstrap):\nCoeff = %.5f\nSE(boot) = %.5f\nt = %.3f\nCI95%% = [%.5f, %.5f]\np = %.5f\n', ...
    n_full, beta_arousal, se_arousal, t_arousal, ci_arousal(1), ci_arousal(2), p_arousal);
 
se_valence = std(boot_beta_valence);
ci_valence = prctile(boot_beta_valence, [2.5 97.5]);
p_valence = 2 * min(mean(boot_beta_valence >= 0), mean(boot_beta_valence <= 0));
t_valence = beta_valence / se_valence;   % pseudo-t: point estimate / bootstrap SE
fprintf('\nPath c (valence, N=%d, bootstrap):\nCoeff = %.5f\nSE(boot) = %.5f\nt = %.3f\nCI95%% = [%.5f, %.5f]\np = %.5f\n', ...
    n_full, beta_valence, se_valence, t_valence, ci_valence(1), ci_valence(2), p_valence);

%% Mediation (paths a, b, c', a*b), SCR-available subsample (n=165)
[paths_arousal, stats_mediation_arousal] = mediation(X_scr, Y_arousal_scr, M_scr, ...
    'plots', 'boot', 'bootsamples', 10000, 'verbose', 'doCIs');

[paths_valence, stats_mediation_valence] = mediation(X_scr, Y_valence_scr, M_scr, ...
    'plots', 'boot', 'bootsamples', 10000, 'verbose', 'doCIs');

%% Save results
if ~exist(savedir, 'dir'); mkdir(savedir); end
save(fullfile(savedir, ['mediation_results_' SIGNATURE '.mat']), ...
    'SIGNATURE', 'full_idx', 'scr_idx', ...
    'boot_beta_arousal', 't_arousal', 'p_arousal', 'stats_mediation_arousal', ...
    'boot_beta_valence', 't_valence', 'p_valence', 'stats_mediation_valence');