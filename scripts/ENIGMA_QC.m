% Image quality check -- one-sample T-test
clear; clc;
basedir = fullfile('.',  'results', 'final_brainmask');
save_results = fullfile(basedir, 'ENIGMA_FC', 'results_QC');

excel = readtable(fullfile(basedir, 'ENIGMA_FC', 'path_info_subj.xlsx'),'VariableNamingRule','preserve');
excel.Properties.RowNames = cellstr(num2str(excel.Var1));

unique_datasets = unique(excel.dataset);

for d = 1:length(unique_datasets)
    d_name = unique_datasets{d};
    subset = excel(strcmp(excel.dataset, d_name), :);

    mkdir(fullfile(save_results, d_name))

    scans = cell(numel(subset.path), 1);
    for i = 1:numel(subset.path)
        scans{i} = [subset.path{i} ',1'];
    end
    matlabbatch{1}.spm.stats.factorial_design.dir = {fullfile(save_results, d_name)};
    matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = scans;
    matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});
    matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});
    matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
    matlabbatch{1}.spm.stats.factorial_design.masking.im = 0; % implicit mask
    matlabbatch{1}.spm.stats.factorial_design.masking.em = {'/Users/acalvet/Documents/MVPA_FISAX/TFM_git/brainmask_canlab_bin_resampled.nii,1'}; % explicit mask si quieres
    matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
    matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
    matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;
    
    % Estimar
    matlabbatch{2}.spm.stats.fmri_est.spmmat(1) = cfg_dep('Factorial design specification: SPM.mat File', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
    matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
    matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;

    % Contraste t positivo (mayor que 0)
    matlabbatch{3}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = 'activation';
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = 1;
    matlabbatch{3}.spm.stats.con.consess{1}.tcon.sessrep = 'none';
    matlabbatch{3}.spm.stats.con.consess{2}.tcon.name = 'deactivation';
    matlabbatch{3}.spm.stats.con.consess{2}.tcon.weights = -1;
    matlabbatch{3}.spm.stats.con.consess{2}.tcon.sessrep = 'none';
    matlabbatch{3}.spm.stats.con.delete = 0;
    
    spm('defaults', 'FMRI');
    spm_jobman('run', matlabbatch);

end


%% OUR
contdirs = dir(fullfile('.', 'contrasts_brainmask'));
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}));
CSpCSn_paths = fullfile('.', 'contrasts_brainmask', list_subj, 'REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL', 'con_0001.nii');

scans = cell(numel(CSpCSn_paths), 1);
for i = 1:numel(CSpCSn_paths)
    scans{i} = [CSpCSn_paths{i} ',1'];
end

matlabbatch{1}.spm.stats.factorial_design.dir = {fullfile(save_results, 'VITS')};
matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = scans;
matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});
matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});
matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
matlabbatch{1}.spm.stats.factorial_design.masking.im = 0; % implicit mask
matlabbatch{1}.spm.stats.factorial_design.masking.em = {'/Users/acalvet/Documents/MVPA_FISAX/TFM_git/brainmask_canlab_bin_resampled.nii,1'}; % explicit mask si quieres
matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;

% Estimar
matlabbatch{2}.spm.stats.fmri_est.spmmat(1) = cfg_dep('Factorial design specification: SPM.mat File', substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;

% Contraste t positivo (mayor que 0)
matlabbatch{3}.spm.stats.con.spmmat(1) = cfg_dep('Model estimation: SPM.mat File', substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}), substruct('.','spmmat'));
matlabbatch{3}.spm.stats.con.consess{1}.tcon.name = 'activation';
matlabbatch{3}.spm.stats.con.consess{1}.tcon.weights = 1;
matlabbatch{3}.spm.stats.con.consess{1}.tcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.consess{2}.tcon.name = 'deactivation';
matlabbatch{3}.spm.stats.con.consess{2}.tcon.weights = -1;
matlabbatch{3}.spm.stats.con.consess{2}.tcon.sessrep = 'none';
matlabbatch{3}.spm.stats.con.delete = 0;

spm('defaults', 'FMRI');
spm_jobman('run', matlabbatch);