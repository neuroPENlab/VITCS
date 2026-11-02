function [ci, auc_boot] = bootstrap_auc_ci(pe_pos, pe_neg, nboot, seed)
%   Participant-level bootstrap 95% CI for the paired-observations AUC.
%
%   BOOTSTRAP_AUC_CI(pe_pos, pe_neg, nboot, seed)
%
% Participants are resampled with replacement and each one keeps BOTH of its
% images (CS+ and CS-), so the within-subject pairing is preserved.
% The AUC is computed with roc_plot exactly as in the training/test scripts.
%
%   INPUTS
%     pe_pos, pe_neg   - n x 1 vectors with the score for CS+ and CS- of the 
%                        SAME participants, in the same order (e.g. cross-validated 
%                        distance from the hyperplane, or pattern expression).
%     nboot            - number of bootstrap samples (default 5000)
%     seed             - random seed (default random value from 1 to 1000)
%   
%   OUTPUTS
%     ci               - 95% confidential intervals
%     auc_boot         - area under the curve (auc)
%
%   If only the CS+ > CS- contrast is available (one value per participant), call
%   bootstrap_auc_ci(contrast, zeros(size(contrast))): roc_plot's paired mode centers
%   each pair, so this gives the same AUC.
%
%   Dependencies: CANlab Core Tools (fmri_data, canlab_pattern_similarity)

if nargin < 3 || isempty(nboot); nboot = 5000; end
if nargin < 4 || isempty(seed);  seed = randi(1000, 1);     end

pe_pos = pe_pos(:);
pe_neg = pe_neg(:);
n = numel(pe_pos);
assert(numel(pe_neg) == n, 'pe_pos and pe_neg must have the same length.');

outcome = [true(n, 1); false(n, 1)];
rng(seed);
auc_boot = nan(nboot, 1);

for b = 1:nboot
    i = randi(n, n, 1);   % participants with replacement
    rp = roc_plot([pe_pos(i); pe_neg(i)], outcome, 'threshold', 'pairedobservations', 'noplot');
    auc_boot(b) = rp.AUC;
end

ci = prctile(auc_boot, [2.5 97.5]);
end