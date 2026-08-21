%% 07_mediation_analysis.m
% -------------------------------------------------------------------
% Test whether skin conductance responses (SCRs) mediate the
% association between VITCS expression during threat acquisition and
% participants' subjective ratings (arousal and valence, separate
% models).
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
% IMPORTANT: path c is computed via a direct regression of Y on X on
% the full N=172 sample. Path c doesn't mathematically depend on M 
% (so the reported number was unaffected), so path c is computed 
% independently and directly instead.
%
% Dependencies: CANlab Mediation Toolbox (mediation.m)
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as previous scripts
basedir = '/Users/acalvet/Repositories/neuroPENlab/VITCS';

scr_path = '<PATH_TO_SCR_DATA>';               % <-- EDIT THIS: SCR_detrend.xlsx equivalent
subj_rat_path = '<PATH_TO_SUBJECTIVE_RATINGS_DATA>'; % <-- EDIT THIS: Subjective_ratings_condrev.xlsx equivalent

%% Define signatures in which apply mediation analysis
signature = 'VITCS'; % EDIT THIS

switch signature
    case 'VITCS'
        pat_exp_path = fullfile(basedir, 'results', 'VITCS_development', 'pat_exp_test_set_VITCS.xlsx');
        savedir = fullfile(basedir, 'results', 'VITCS_mediation');
    case 'Reddan'
        pat_exp_path = fullfile();
        savedir = fullfile(basedir, 'results', 'comparison_existing_signatures');
    case 'SUITAS'
        pat_exp_path = fullfile();
        savedir = fullfile(basedir, 'results', 'comparison_existing_signatures');
    case 'VITCS-early'
        pat_exp_path = fullfile(basedir, 'results', 'VITCS_early_results', 'pat_exp_test_set_VITCS.xlsx');
        savedir = fullfile(basedir, 'results', 'VITCS_early_results');
    case 'VITCS-late'
        pat_exp_path = fullfile(basedir, 'results', 'VITCS_late_results', 'pat_exp_test_set_VITCS.xlsx');
        savedir = fullfile(basedir, 'results', 'VITCS_late_results');
end

%% Load data
skin = readtable(scr_path, 'ReadRowNames', true);
subj_rat = readtable(subj_rat_path, 'ReadRowNames', true);

skin_sub = skin(:, 'Cond_CSplus_mean');
skin_sub.Properties.VariableNames = cols_pat_exp;

subj_rat_sub = subj_rat(:, {'COND_CSplus_ARO', 'COND_CSplus_VAL'});


pat_exp = readtable(pat_exp_path, 'ReadRowNames', true, 'VariableNamingRule', 'preserve');
pat_exp.Properties.RowNames = erase(pat_exp.Properties.RowNames, "sub-");
pat_exp_sub = pat_exp(:, [signature '_CS+']);

%% Build the two samples: full (N=172) and SCR-available (n=165)
full_idx = intersect(pat_exp.Properties.RowNames, subj_rat.Properties.RowNames);   % pattern expression + ratings
scr_idx  = intersect(full_idx, skin.Properties.RowNames);                          % + usable SCR

fprintf('Full sample (pattern expression + ratings): N = %d\n', length(full_idx));
fprintf('SCR-available subsample: n = %d\n', length(scr_idx));

pat_exp_full = pat_exp_sub(full_idx, :);
subj_rat_full = subj_rat_sub(full_idx, :);

pat_exp_scr = pat_exp_sub(scr_idx, :);
subj_rat_scr = subj_rat_sub(scr_idx, :);
skin_scr = skin_sub(scr_idx, :);

%% Define X (VITCS), M (SCR) for the mediation model
X_full = pat_exp_full.([signature '_CS+']);
X_scr  = pat_exp_scr.([signature '_CS+']); 
M_scr  = skin_scr.Cond_CSplus_mean; 

% Y: arousal and valence, as two separate models (valence reverse-coded
% so higher = more negative, matching "perceived negative valence").
Y_arousal_full = subj_rat_full.COND_CSplus_ARO;
Y_valence_full = (subj_rat_full.COND_CSplus_VAL - 6) * -1;

Y_arousal_scr = subj_rat_scr.COND_CSplus_ARO;
Y_valence_scr = (subj_rat_scr.COND_CSplus_VAL - 6) * -1;

%% Path c: total effect of VITCS on subjective ratings, full sample (N=172)
% Direct regression, Y ~ X - no mediator involved.
x_design = [ones(size(X_full)) X_full];

[beta_arousal, ~, ~, ~, stats_arousal] = regress(Y_arousal_full, x_design);
XtX_inv = inv(x_design' * x_design);
se_arousal = sqrt(stats_arousal(4) * XtX_inv(2, 2));
t_arousal = beta_arousal(2) / se_arousal;
fprintf('\nPath c (arousal, N=%d):\nCoeff = %.5f\nSE = %.5f\nt = %.3f\np = %.5f\n', ...
    length(full_idx), beta_arousal(2), se_arousal, t_arousal, stats_arousal(3));

[beta_valence, ~, ~, ~, stats_valence] = regress(Y_valence_full, x_design);
se_valence = sqrt(stats_valence(4) * XtX_inv(2, 2));
t_valence = beta_valence(2) / se_valence;
fprintf('\nPath c (valence, N=%d):\nCoeff = %.5f\nSE = %.5f\nt = %.3f\np = %.5f\n', ...
    length(full_idx), beta_valence(2), se_valence, t_valence, stats_valence(3));

%% Mediation (paths a, b, c', a*b), SCR-available subsample (n=165)
[paths_arousal, stats_mediation_arousal] = mediation(X_scr, Y_arousal_scr, M_scr, ...
    'plots', 'boot', 'bootsamples', 10000, 'verbose', 'doCIs');

[paths_valence, stats_mediation_valence] = mediation(X_scr, Y_valence_scr, M_scr, ...
    'plots', 'boot', 'bootsamples', 10000, 'verbose', 'doCIs');

%% Save results
if ~exist(savedir, 'dir'); mkdir(savedir); end
save(fullfile(savedir, 'mediation_results.mat'), 'full_idx', 'scr_idx', ...
    'beta_arousal', 'se_arousal', 't_arousal', 'stats_arousal', ...
    'beta_valence', 'se_valence', 't_valence', 'stats_valence', ...
    'paths_arousal', 'stats_mediation_arousal', ...
    'paths_valence', 'stats_mediation_valence');