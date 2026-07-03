#!/usr/bin/env bash
# Usage:
#   ./prune_clusters.sh <BASE> <REF> <OUT> [MIN_FRAC] [MIN_VOX]
# Example:
#   ./prune_clusters.sh unc001_pos_bin.nii.gz FDR05_pos_bin.nii.gz UNC001_pos_prunedfdr05_pos.nii.gz 0.00 1
#   ./prune_clusters.sh unc01_pos_bin.nii.gz FDR05_pos_bin.nii.gz UNC01_pos_prunedfdr05_pos.nii.gz 0.05 10

# bash cluster_prunning.sh /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/unc001_pos.nii.gz /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/fdr05_pos.nii.gz /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/UNC001_pos_prunedfdr05_pos.nii.gz 0.00 1
# bash cluster_prunning.sh /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/unc01_pos.nii.gz /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/fdr05_pos.nii.gz /Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai_sex/reliable_anatomy/UNC01_pos_prunedfdr05_pos.nii.gz 0.00 1

set -euo pipefail

BASE="$1"       # màscara a prunejar
REF="$2"        # màscara de referència (criteri)
OUT="$3"        # sortida: base prunejada (cluster-wise)
MIN_FRAC="${4:-0.00}"  # fracció mínima d'overlap respecte el clúster de BASE (0.00 = n/a)
MIN_VOX="${5:-1}"      # # mínim de voxels d'overlap (1 = almenys 1 voxel)

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# 0) Assegura binàries
fslmaths "$BASE" -bin "$tmpdir/base_bin"
fslmaths "$REF"  -bin "$tmpdir/ref_bin"

# 1) Etiqueta clústers a la BASE
cluster --in="$tmpdir/base_bin" --thresh=0.5 --oindex="$tmpdir/base_idx" >/dev/null

# 2) Troba el # màxim d'etiqueta
MAXLAB=$(fslstats "$tmpdir/base_idx" -R | awk '{printf "%.0f", $2}')
# Inicialitza OUT a zeros amb la mateixa geometria
fslmaths "$tmpdir/base_bin" -mul 0 "$OUT"

# 3) Itera per clústers
for (( i=1; i<=MAXLAB; i++ )); do
  # màscara del clúster i
  fslmaths "$tmpdir/base_idx" -thr $i -uthr $i -bin "$tmpdir/ci"

  # mida del clúster (en voxels)
  BASE_VOX=$(fslstats "$tmpdir/ci" -V | awk '{print $1}')
  if [ "$BASE_VOX" -eq 0 ]; then
    continue
  fi

  # overlap en voxels amb REF
  fslmaths "$tmpdir/ci" -mas "$tmpdir/ref_bin" "$tmpdir/ov"
  OV_VOX=$(fslstats "$tmpdir/ov" -V | awk '{print $1}')

  # fracció d'overlap respecte el clúster de BASE
  OV_FRAC=0
  if [ "$BASE_VOX" -gt 0 ]; then
    OV_FRAC=$(awk -v a="$OV_VOX" -v b="$BASE_VOX" 'BEGIN{ if(b>0) printf "%.6f", a/b; else print "0"; }')
  fi

  # Criteri: (almenys MIN_VOX) i (almenys MIN_FRAC)
  pass_vox=$(awk -v o="$OV_VOX" -v m="$MIN_VOX" 'BEGIN{ print (o>=m) ? 1 : 0 }')
  pass_frac=$(awk -v f="$OV_FRAC" -v m="$MIN_FRAC" 'BEGIN{ print (f+1e-12>=m) ? 1 : 0 }')

  if [ "$pass_vox" -eq 1 ] && [ "$pass_frac" -eq 1 ]; then
    # Conservar TOT el clúster i (no només l'overlap)
    fslmaths "$OUT" -add "$tmpdir/ci" "$OUT"
  fi
done

# Binaritza resultat per seguretat
fslmaths "$OUT" -bin "$OUT"
echo "Done -> $OUT"
