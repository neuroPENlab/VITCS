clear; clc;
basedir = fullfile('.', 'results', 'final_brainmask', 'comparison_zscores_signatures');
maskdir = fullfile('.', 'brainmask_canlab_bin_resampled.nii');
corr_roisdir = fullfile('.','results', 'final_brainmask', '2_SVM_results_stai', 'PLOTS_poster');

res_corr = array2table(zeros(3, 6), 'VariableNames', {'R_wholebrain', ...
    'R_clust1', 'R_clust2', 'R_clust3', 'R_clust4', 'R_clust5'}, 'RowNames', ...
    {'VITS_THREAT', 'VITS_THREAT_Z', 'VITS_SUITAS'});

% Load brain signatures
[vits, ] = load_image_set({fullfile(basedir, 'svm_results_unthresholded.nii')});
[vits_z, ] = load_image_set({fullfile(basedir, 'svm_results_unthresholded_zscore.nii')});
[threat, ] = load_image_set({fullfile(basedir, 'IE_ImEx_Acq_Threat_SVM_nothresh.nii')});
[threat_z, ] = load_image_set({fullfile(basedir, 'IE_ImEx_Acq_Threat_SVM_nothresh_zscore.nii')});
[suitas, ] = load_image_set({fullfile(basedir, 'Induced20_z.nii')});

threat = resample_space(threat, vits);
threat_z = resample_space(threat_z, vits);
suitas = resample_space(suitas, vits);

%% Neurosynth mask
neurosynth_mask = fullfile('.','results', 'final_brainmask', 'neurosynth_masks');
[vits_nsytn, ~] = apply_mask(vits, fullfile(neurosynth_mask, 'neurosynth_mask_dil_resampled_cl01.nii.gz'));
[vits_z_nsytn, ~] = apply_mask(vits_z, fullfile(neurosynth_mask, 'neurosynth_mask_dil_resampled_cl01.nii.gz'));
[threat_nsytn, ~] = apply_mask(threat, fullfile(neurosynth_mask, 'neurosynth_mask_dil_resampled_cl01.nii.gz'));
[threat_z_nsytn, ~] = apply_mask(threat_z, fullfile(neurosynth_mask, 'neurosynth_mask_dil_resampled_cl01.nii.gz'));
[suitas_nsytn, ~] = apply_mask(suitas, fullfile(neurosynth_mask, 'neurosynth_mask_dil_resampled_cl01.nii.gz'));

vits_threat_nsytn_corr = image_similarity_plot(vits_nsytn, 'mapset', threat_nsytn, 'networknames', {'threat'});
vits_threat_z_nsytn_corr = image_similarity_plot(vits_z_nsytn, 'mapset', threat_z_nsytn, 'networknames', {'threat_z'});
vits_suitas_nsytn_corr = image_similarity_plot(vits_z_nsytn, 'mapset', suitas_nsytn, 'networknames', {'suitas'});
%%%%%

%% Correlation
vits_threat_corr = image_similarity_plot(vits, 'mapset', [threat], 'networknames', {'threat'});
res_corr{'VITS_THREAT','R_wholebrain'} = vits_threat_corr.r;
vits_z_corr = image_similarity_plot(vits_z, 'mapset', [threat_z, suitas], ...
    'networknames', {'threat-z', 'suitas'});
res_corr{'VITS_THREAT_Z','R_wholebrain'} = vits_z_corr.r(1);
res_corr{'VITS_SUITAS','R_wholebrain'} = vits_z_corr.r(2);

clusters = {'cl1_fdr05.nii', 'cl2_fdr05.nii', 'cl3_fdr05.nii', 'cl4_fdr05.nii', 'cl5_fdr05.nii'};
for cl = 1:5
    [vits_roi, ~] = apply_mask(vits, fullfile(corr_roisdir, clusters{cl}));
    [vits_z_roi, ~] = apply_mask(vits_z, fullfile(corr_roisdir, clusters{cl}));
    [threat_roi, m1] = apply_mask(threat, fullfile(corr_roisdir, clusters{cl}));
    % if length(m1.dat) ~= length(m1.removed_voxels)
    %     dat = zeros(size(~m1.removed_voxels));
    %     dat(~m1.removed_voxels) = threat_roi.dat;
    %     threat_roi.dat = dat;
    % end
    [threat_z_roi, m2] = apply_mask(threat_z, fullfile(corr_roisdir, clusters{cl}));
    [suitas_roi, m3] = apply_mask(suitas, fullfile(corr_roisdir, clusters{cl}));

    vits_threat_corr = image_similarity_plot(vits_roi, 'mapset', threat_roi, 'networknames', {'threat'});
    res_corr{'VITS_THREAT',['R_clust' num2str(cl)]} = vits_threat_corr.r;
    vits_threatz_corr = image_similarity_plot(vits_z_roi, 'mapset', threat_z_roi, 'networknames', {'threat-z'});
    res_corr{'VITS_THREAT_Z',['R_clust' num2str(cl)]} = vits_threatz_corr.r;
    vits_suitas_corr = image_similarity_plot(vits_z_roi, 'mapset', suitas_roi, 'networknames', {'suitas'});
    res_corr{'VITS_SUITAS',['R_clust' num2str(cl)]} = vits_suitas_corr.r;
    close all;
end
writetable(res_corr, fullfile(basedir, 'correlation_similarity_comparison.xlsx'), "WriteRowNames",true)
%%
[stats, hh, hhfill, table_group, multcomp_group] = image_similarity_plot(our, 'mapset', [threat, suitas], ...
    'networknames', {'threat', 'suitas'});

% Match analysis
our_pos = threshold(vits, [-Inf 2.3], 'raw-outside');
our_neg = threshold(vits, [-2.3 Inf], 'raw-outside');
our_thr = threshold(vits, [-2.3 2.3], 'raw-outside');

threat_pos = threshold(threat, [-Inf 2.3], 'raw-outside');
threat_neg = threshold(threat, [-2.3 Inf], 'raw-outside');
threat_thr = threshold(threat, [-2.3 2.3], 'raw-outside');

suitas_pos = threshold(suitas, [-Inf 2.3], 'raw-outside');
suitas_neg = threshold(suitas, [-2.3 Inf], 'raw-outside');
suitas_thr = threshold(suitas, [-2.3 2.3], 'raw-outside');

orthviews(threat_thr);
orthviews(our_thr);
orthviews(threat_res);

% Save images
our_thr.fullpath = fullfile(basedir, 'from_matlab', 'our_thr.nii');
write(our_thr);
threat_thr.fullpath = fullfile(basedir, 'from_matlab', 'threat_thr.nii');
write(threat_thr);
suitas_thr.fullpath = fullfile(basedir, 'from_matlab', 'suitas_thr.nii');
write(suitas_thr);

our_pos.fullpath = fullfile(basedir, 'from_matlab', 'our_pos.nii');
write(our_pos);
threat_pos.fullpath = fullfile(basedir, 'from_matlab', 'threat_pos.nii');
write(threat_pos);
suitas_pos.fullpath = fullfile(basedir, 'from_matlab', 'suitas_pos.nii');
write(suitas_pos);

our_neg.fullpath = fullfile(basedir, 'from_matlab', 'our_neg.nii');
write(our_neg);
threat_neg.fullpath = fullfile(basedir, 'from_matlab', 'threat_neg.nii');
write(threat_neg);
suitas_neg.fullpath = fullfile(basedir, 'from_matlab', 'suitas_neg.nii');
write(suitas_neg);

% Reload images
[our_thr2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'our_thr.nii')});
[threat_thr2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'threat_thr.nii')});
[suitas_thr2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'suitas_thr.nii')});

[our_pos2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'our_pos.nii')});
[threat_pos2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'threat_pos.nii')});
[suitas_pos2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'suitas_pos.nii')});

[our_neg2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'our_neg.nii')});
[threat_neg2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'threat_neg.nii')});
[suitas_neg2, ] = load_image_set({fullfile(basedir, 'from_matlab', 'suitas_neg.nii')});

% Union / intersection
[datu, dati_pos_our_threat] = union(our_pos2, threat_pos2);
[datu, dati_neg_our_threat] = union(our_neg2, threat_neg2);
[datu, dati_pos_our_suitas] = union(our_pos2, suitas_pos2);
[datu, dati_neg_our_suitas] = union(our_neg2, suitas_neg2);

% dati_pos_our_threat.fullpath = fullfile(basedir, 'from_matlab', 'dati_pos_our_threat.nii');
% write(dati_pos_our_threat);
% dati_neg_our_threat.fullpath = fullfile(basedir, 'from_matlab', 'dati_neg_our_threat.nii');
% write(dati_neg_our_threat);
% dati_pos_our_suitas.fullpath = fullfile(basedir, 'from_matlab', 'dati_pos_our_suitas.nii');
% write(dati_pos_our_suitas);
% dati_neg_our_suitas.fullpath = fullfile(basedir, 'from_matlab', 'dati_neg_our_suitas.nii');
% write(dati_neg_our_suitas);


%% Fem altres coses: promig de weights (z-score) del clusters més representatius + correlacion
atlas_2023 = load_atlas('canlab2023_coarse_fmriprep20_2mm').threshold(0.2);

order_sig = {{vits, threat, suitas}, {threat, vits, suitas}, {suitas, vits, threat}};
order_table = {{'VITS', 'THREAT', 'SUITAS', 'Labels'}, ...
    {'THREAT', 'VITS', 'SUITAS', 'Labels'}, {'SUITAS', 'VITS', 'THREAT', 'Labels'}};

for i = 1:length(order_sig)
    signatures = order_sig{i};
    col_n = order_table{i};

    % Zones més significatives
    sig_sigZ = threshold(signatures{1}, [-2.3 2.3], 'raw-outside', 'k', 50);
    % sig_sigZ = threshold(signatures{1}, [-2 2], 'raw-outside', 'k', 50);
    sig_sigZ.fullpath = fullfile(basedir, 'NEW_z2.3', [col_n{1} '_zscore2_3_k50.nii']);
    % write(sig_sigZ);
    % orthviews(sig_sigZ);

    % Seprarar per clusters/regions
    sig_sigZ_clust = region(sig_sigZ);

    row_n = arrayfun(@(i) ['Cluster' num2str(i)], 1:length(sig_sigZ_clust), 'UniformOutput', false);
    res_mean = array2table(nan(numel(row_n), numel(col_n)), 'VariableNames', col_n, 'RowNames', row_n);
    res_corr = array2table(nan(numel(row_n), numel(col_n)), 'VariableNames', col_n, 'RowNames', row_n);
    res_mean.Labels = cell(height(res_mean), 1);
    res_corr.Labels = cell(height(res_corr), 1);

    for c = 1:length(sig_sigZ_clust)
        reg = sig_sigZ_clust(c);

        % create nifti with clusters
        reg2fmri = region2fmri_data(reg, signatures{1});
        for t =  1:c
            if t == 1 && c == 1
                all_reg = reg2fmri;
            else
                all_reg = image_math(all_reg, 'add', reg2fmri);
            end
        end
        % orthviews(all_reg);
        if c == 1
            data_4D = reg2fmri;
        else
            data_4D.dat = cat(2, data_4D.dat, reg2fmri.dat);
        end

        [region_1, corr_1] = extract_data(reg, signatures{1}, 'correlation');
        res_mean{['Cluster' num2str(c)], col_n{1}} = region_1.dat;
        res_corr{['Cluster' num2str(c)], col_n{1}} = corr_1{1};
        [region_2, corr_2] = extract_data(reg, signatures{2}, 'correlation');
        res_mean{['Cluster' num2str(c)], col_n{2}} = region_2.dat;
        res_corr{['Cluster' num2str(c)], col_n{2}} = corr_2{1};
        [region_3, corr_3] = extract_data(reg, signatures{3}, 'correlation');
        res_mean{['Cluster' num2str(c)], col_n{3}} = region_3.dat;
        res_corr{['Cluster' num2str(c)], col_n{3}} = corr_3{1};
        
        % orthviews(reg);
        % r = gcf;
        % saveas(r, fullfile(basedir, 'NEW_z2.3', [col_n{1} '_region_' num2str(c) '.png']))
        % close(r);
    
        reg_atlas = extract_data(reg, atlas_2023);
        labels_reg = tabulate(reg_atlas.all_data);
        labels_reg(labels_reg(:,1) == 0,:) = [];
        labels_reg = sortrows(labels_reg, 3, 'descend');
        label_name = atlas_2023.labels_3(labels_reg(:,1));
        % 1st = unique values of X; 2nd = #instances of each value. 3rd = %each value
    
        results = cell(size(labels_reg, 1), 1);
        for j = 1:size(labels_reg, 1)
            %results{j} = sprintf('%s (%.2f%%)', ['Label ' num2str(labels_reg(j, 1))], labels_reg(j, 3));
            results{j} = sprintf('%s (%.2f%%)', label_name{j}, labels_reg(j, 3));
        end
        res_mean{['Cluster' num2str(c)], 'Labels'} = {strjoin(results', ', ')};
        res_corr{['Cluster' num2str(c)], 'Labels'} = {strjoin(results', ', ')};
    end

    % data_4D.fullpath = fullfile(basedir, 'NEW_z2.3', [col_n{1} '_regions_4D.nii']);
    % write(data_4D, 'thresh');
    all_reg.fullpath = fullfile(basedir, 'NEW_z2.3', [col_n{1} '_regions_labels.nii']);
    write(all_reg, 'thresh');

    % fig1 = figure('Position', [100, 100, 900, 600], 'Visible', 'off');
    % for col = col_n(1:end-1)
    %     plot(1:length(sig_sigZ_clust), res_mean{:, col{1}}, '-o', 'LineWidth', 2, 'MarkerSize', 8);
    %     hold on;
    % end
    % xlabel([col_n{1} ' regions']);
    % ylabel('Mean value');
    % title(['Mean value of each cluster from ' col_n{1} ' in each signature']);
    % legend(col_n);
    % grid on;
    % hold off;
    % saveas(fig1, fullfile(basedir, 'NEW_z2.3', ['mean_' col_n{1} '.png']));
    % close(fig1);
    % 
    % fig2 = figure('Visible', 'off'); 
    % h=heatmap(res_corr{:,2:3}, 'XData', {col_n{2}, col_n{3}});
    % colormap(h, "jet");
    % xlabel('Signatures');
    % ylabel([col_n{1} ' clusters']);
    % title(['Correlation between ' col_n{1} ' and other signatures']);
    % saveas(fig2, fullfile(basedir, 'NEW_z2.3', ['corr_' col_n{1} '.png']));
    % close(fig2);
end
