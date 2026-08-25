function run_bootstrap_feature_stability(basedir, CSp_paths, CSm_paths, output_dir)
%   Bootstrap feature-stability analysis for a VITCS-family model.
%   Identify brain regions that most reliably contribute to classification.
%
%   RUN_BOOTSTRAP_FEATURE_STABILITY(basedir, CSp_paths, CSm_paths, output_dir)
%
%   Shared bootstrap routine used for the main VITCS model and the
%   VITCS-early / VITCS-late variants (Supplementary Text, "SVM
%   classification and Bootstrap Inference": bootstrap resampling is
%   also referenced for the stage-specific models) - same procedure,
%   only the input contrast images differ.
%
%   From Methods: "In order to identify the brain regions that most
%   significantly and reliably contributed to the VITCS threat-safety
%   classification, we conducted a bootstrap analysis with 5,000
%   resamples (with replacement) and applied false discovery rate (FDR)
%   correction for thresholding." Uncorrected thresholds (p < .001 and
%   p < .01) are additionally saved for visualization purposes in
%   datasets where no voxels survive whole-brain FDR correction
%   (Supplementary Fig. 6).
%
%   INPUTS
%       basedir     - project root (same BASEDIR used by the caller)
%       CSp_paths    - cell array with all CS+ contrast paths
%       CSm_paths    - cell array with all CS- contrast paths
%       output_dir  - directory to write this model's bootstrap outputs to
%
%   Expects data/training_data.mat to already exist under basedir/data
%   (see 01_train_test_split.m).
%
%   Dependencies: CANlab Core Tools (fmri_data, predict, threshold, write)

if ~exist(output_dir, 'dir'); mkdir(output_dir); end

%% Paths
datadir = fullfile(basedir, 'data');
maskdir = fullfile(datadir, 'brainmask.nii');

%% Load training data 
tr_set = load(fullfile(datadir, 'training_data.mat')).tr_set;

training_data = fmri_data([CSp_paths(tr_set), CSm_paths(tr_set)], maskdir);
training_data.Y = [ones(sum(tr_set), 1); -ones(sum(tr_set), 1)];

%% Bootstrap resampling (5,000 samples) 
[~, stats_boot] = predict(training_data, 'algorithm_name', 'cv_svm', 'nfolds', 1, ...
    'C', 1, 'error_type', 'mcr', 'bootweights', 'bootsamples', 5000);

% Save stats_boot
save(fullfile(output_dir, 'stats_bootstrap.mat'), 'stats_boot');

%% Threshold the bootstrapped weight map 
boot_fdr05  = threshold(stats_boot.weight_obj, .05,  'fdr', 'mask', maskdir);
boot_unc001 = threshold(stats_boot.weight_obj, .001, 'unc', 'mask', maskdir);
boot_unc01  = threshold(stats_boot.weight_obj, .01,  'unc', 'mask', maskdir);

%% Save thresholded maps 
boot_fdr05.fullpath = fullfile(output_dir, 'VITCS_bootstrap_fdr05.nii');
write(boot_fdr05, 'thresh');

boot_unc001.fullpath = fullfile(output_dir, 'VITCS_bootstrap_unc001.nii');
write(boot_unc001, 'thresh');

boot_unc01.fullpath = fullfile(output_dir, 'VITCS_bootstrap_unc01.nii');
write(boot_unc01, 'thresh');

end