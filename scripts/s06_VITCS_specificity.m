%% s06_VITCS_specificity.m
% -------------------------------------------------------------------
% Evaluate the specificity of VITCS with respect to reward processing,
% using two independent reward-related datasets.
%
% From Methods: "To assess the specificity of the VITCS, we applied
% the signature to two reward-related datasets: 1) Monetary Incentive
% Delay (MID) dataset (N = 39 healthy women) [...] comparing CueGain
% and CueLoss conditions using within-subject contrast maps; 2) Human
% Connectome Project Young Adult study (HCP-YA; N = 1,061 healthy
% adults) [...] the reward vs. punishment contrast, from the
% Gambling/Incentive task. For both contrasts, VITCS pattern expression
% was quantified using two similarity metrics: (i) the dot product and
% (ii) cosine similarity [...]. Discriminative performance was
% evaluated using a within-subject forced-choice classification
% framework [...]. Statistical significance of forced-choice accuracy
% was assessed against chance (50%) using a binomial test, as
% implemented in the roc_plot function (CanlabCore toolbox). Effect
% size was quantified as Cohen's d on the within-subject difference
% scores."
%
% Dependencies: CANlab Core Tools (fmri_data, canlab_pattern_similarity,
%               roc_plot)
% -------------------------------------------------------------------
clear; clc;

%% User-defined paths (TO EDIT)
basedir = '<PATH_TO_PROJECT>';   % <-- EDIT THIS, same as previous scripts
datadir = fullfile(basedir, 'data');   % <-- if necessary, EDIT THIS
sigdir  = fullfile(basedir, 'results', 'VITCS_development');
savedir = fullfile(basedir, 'results', 'VITCS_specificity');
if ~exist(savedir, 'dir'); mkdir(savedir); end

maskdir = fullfile(datadir, 'brainmask.nii');

metrics = {'dot_product', 'cosine_similarity'};

%% Load the VITCS signature
VITCS_sig = fmri_data(fullfile(sigdir, 'VITCS_unthresholded_10foldCV.nii'), maskdir);

%% Results table (both datasets x both metrics)
row_names = {'CueGainVSCueLoss_dotproduct', 'CueGainVSCueLoss_cosine', ...
             'RewardVSpunishment_dotproduct', 'RewardVSpunishment_cosine'};
res_specificity = array2table(nan(4, 5), ...
    'VariableNames', {'accuracy', 'sensitivity', 'specificity', 'p-value', 'cohens_d'});
res_specificity.Properties.RowNames = row_names;

%% -----------------------------------------------------------------------------
%% 1) Monetary Incentive Delay (MID) task - N = 39
%% -----------------------------------------------------------------------------
% Define paths
list_subj_mid = {}; % <-- EDIT THIS: list of MID subject IDs (N=39)
contrastdir_mid = '<PATHS_TO_MID_CONTRAST_DATA>'; % <-- EDIT THIS
contrast_subpath_mid = '<SUBPATH_TO_MID_STATS_FOLDER>'; % <-- EDIT THIS, e.g. fullfile('stats_mid')

cuegain_file = '<name_CueGain_contrast_file>'; % <-- EDIT THIS, e.g. 'con_0005'
cueloss_file = '<name_CueLoss_contrast_file>'; % <-- EDIT THIS, e.g. 'con_0006'

cuegain_paths = fullfile(contrastdir_mid, list_subj_mid, contrast_subpath_mid, [cuegain_file '.nii']);
cueloss_paths = fullfile(contrastdir_mid, list_subj_mid, contrast_subpath_mid, [cueloss_file '.nii']);

% Load contrast data
data_cuegain = fmri_data(cuegain_paths, maskdir);
data_cueloss = fmri_data(cueloss_paths, maskdir);

% Resample signature to contrast data space
VITCS_resampled_mid = resample_space(VITCS_sig, data_cuegain);

% Calculate pattern expression
for m = 1:length(metrics)
    metric = metrics{m};
    row = row_names{m};   % rows 1-2: dot product, cosine similarity

    pat_exp_cuegain = canlab_pattern_similarity(data_cuegain.dat, VITCS_resampled_mid.dat, metric);
    pat_exp_cueloss = canlab_pattern_similarity(data_cueloss.dat, VITCS_resampled_mid.dat, metric);

    rp = roc_plot([pat_exp_cuegain; pat_exp_cueloss], ...
        [ones(length(pat_exp_cuegain), 1); zeros(length(pat_exp_cueloss), 1)], ...
        'threshold', 'pairedobservations');

    dif_mid = pat_exp_cuegain - pat_exp_cueloss;
    d = mean(dif_mid) / std(dif_mid); % Cohen's D

    res_specificity{row, :} = [rp.accuracy, rp.sensitivity, rp.specificity, rp.accuracy_p, d];
end

%% -----------------------------------------------------------------------------
%% 2) Human Connectome Project Young Adult (HCP-YA) - N = 1,061
%% -----------------------------------------------------------------------------
% Precomputed VITCS pattern expression scores for the HCP-YA
% Gambling/Incentive task (Reward vs. punishment contrast), provided by
% the HCP-YA collaborators (T. Wager) - not raw contrast images.
hcp_scores_path = '<PATH_TO_HCP_VITCS_SCORES>'; % <-- EDIT THIS, e.g. fullfile(datadir, 'VITCS_scores_HCP.mat')
VITCS_scores = load(hcp_scores_path).VITCS_scores;

reward_v_punish = VITCS_scores.condition_scores{2};          % [:,1]=reward, [:,2]=punish; dot product
reward_v_punish_cos = VITCS_scores.condition_scores_cosine{2}; % same, cosine similarity

hcp_data = {reward_v_punish, reward_v_punish_cos};

for m = 1:length(metrics)
    row = row_names{2 + m};   % rows 3-4: dot product, cosine similarity
    scores = hcp_data{m};

    rp = roc_plot([scores(:, 1); scores(:, 2)], ...
        [ones(size(scores, 1), 1); zeros(size(scores, 1), 1)], ...
        'threshold', 'pairedobservations');

    dif_hcp = scores(:, 1) - scores(:, 2);
    d = mean(dif_hcp) / std(dif_hcp); % Cohen's D

    res_specificity{row, :} = [rp.accuracy, rp.sensitivity, rp.specificity, rp.accuracy_p, d];
end

%% Save results
writetable(res_specificity, fullfile(savedir, 'specificity_results.csv'), 'WriteRowNames', true);
disp(res_specificity);

save(fullfile(savedir, 'specificity_results.mat'), ...
    'res_specificity', 'pat_exp_cuegain', 'pat_exp_cueloss', 'reward_v_punish', 'reward_v_punish_cos');