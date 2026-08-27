#!/usr/bin/env bash
# Usage:
#   ./fig_2_cluster_prunning.sh  <BASE>  <REF>  <OUT>  [MIN_FRAC]  [MIN_VOX]
# Example:
#   ./fig_2_cluster_prunning.sh unc001_pos_bin.nii.gz FDR05_pos_bin.nii.gz UNC001_prunedfdr05_pos.nii.gz 0.00 1

set -euo pipefail

BASE="$1"       # mask to prune
REF="$2"        # reference mask (criterion)
OUT="$3"        # output: pruned base mask (cluster-wise)
MIN_FRAC="${4:-0.00}"  # minimum overlap fraction relative to each BASE cluster (0.00 = n/a)
MIN_VOX="${5:-1}"      # minimum number of overlapping voxels (1 = at least 1 voxel)

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# 0) Ensure binary masks
fslmaths "$BASE" -bin "$tmpdir/base_bin"
fslmaths "$REF"  -bin "$tmpdir/ref_bin"

# 1) Label clusters in BASE
cluster --in="$tmpdir/base_bin" --thresh=0.5 --oindex="$tmpdir/base_idx" >/dev/null

# 2) Find the maximum cluster label
MAXLAB=$(fslstats "$tmpdir/base_idx" -R | awk '{printf "%.0f", $2}')
# Inicialitza OUT a zeros amb la mateixa geometria
fslmaths "$tmpdir/base_bin" -mul 0 "$OUT"

# 3) Iterate over clusters
for (( i=1; i<=MAXLAB; i++ )); do
  # mask for cluster i
  fslmaths "$tmpdir/base_idx" -thr $i -uthr $i -bin "$tmpdir/ci"

  # cluster size (in voxels)
  BASE_VOX=$(fslstats "$tmpdir/ci" -V | awk '{print $1}')
  if [ "$BASE_VOX" -eq 0 ]; then
    continue
  fi

  # overlap in voxels with REF
  fslmaths "$tmpdir/ci" -mas "$tmpdir/ref_bin" "$tmpdir/ov"
  OV_VOX=$(fslstats "$tmpdir/ov" -V | awk '{print $1}')

  # overlap fraction relative to the BASE cluster
  OV_FRAC=0
  if [ "$BASE_VOX" -gt 0 ]; then
    OV_FRAC=$(awk -v a="$OV_VOX" -v b="$BASE_VOX" 'BEGIN{ if(b>0) printf "%.6f", a/b; else print "0"; }')
  fi

  # Criterion: (at least MIN_VOX) and (at least MIN_FRAC)
  pass_vox=$(awk -v o="$OV_VOX" -v m="$MIN_VOX" 'BEGIN{ print (o>=m) ? 1 : 0 }')
  pass_frac=$(awk -v f="$OV_FRAC" -v m="$MIN_FRAC" 'BEGIN{ print (f+1e-12>=m) ? 1 : 0 }')

  if [ "$pass_vox" -eq 1 ] && [ "$pass_frac" -eq 1 ]; then
    # Keep the ENTIRE cluster i (not just the overlapping part)
    fslmaths "$OUT" -add "$tmpdir/ci" "$OUT"
  fi
done

# Binarize the result for safety
fslmaths "$OUT" -bin "$OUT"
echo "Done -> $OUT"
