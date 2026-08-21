#!/usr/bin/env bash
# Separate positive and negative clusters and binarize them
#
# Usage:
#   ./process_reliable_anatomy.sh <input_image> <output_name_positive> <output_name_negative>
#
# Example:
#   ./process_reliable_anatomy.sh \
#       path/to/clusterimage.nii.gz \
#       path/to/clusterimage_pos_bin.nii.gz \
#       path/to/clusterimage_neg_bin.nii.gz


# bash process_reliable_anatomy.sh /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/unc001_pos.nii.gz /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/fdr05_pos.nii.gz /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/UNC001_pos_prunedfdr05_pos.nii.gz 0.00 1

set -e

input_image="$1"
output_image_pos="$2"
output_image_neg="$3"

# Check that all arguments were provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_image> <output_image_positive> <output_image_negative>"
    exit 1
fi

# Positive clusters: threshold > 0 and binarize
fslmaths "$input_image" -thr 0 -bin "$output_image_pos"

# Negative clusters: threshold < 0, take absolute value, and binarize
fslmaths "$input_image" -uthr 0 -abs -bin "$output_image_neg"

echo "Done!"
echo "Positive: $output_image_pos"
echo "Negative: $output_image_neg"