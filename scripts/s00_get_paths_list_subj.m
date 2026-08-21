function s00_get_paths_list_subj(contrastdir)
% Fer una funció que cridi cada vegada i així només s'ha de canviar un cop
% no?

% contrastdir = '<PATHS_TO_CONTRAST_DATA>';

contrast_subpath = fullfile('REVERSAL', 'FIRST_LEVEL_REVERSAL_Half_ALL'); % <-- EDIT IF YOUR FOLDER STRUCTURE DIFFERS

contdirs = dir(contrastdir);
list_subj = {contdirs([contdirs.isdir]).name};
list_subj = list_subj(~ismember(list_subj, {'.', '..'}))';
end