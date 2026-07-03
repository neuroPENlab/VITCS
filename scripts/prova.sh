#!/bin/bash

# -------- CONFIGURACIÓN --------
IMG="/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/svm_bootstrap_fdr05_nt.nii"
THR=1e-17
ATLAS="/Users/acalvet/Documents/MVPA_FISAX/DATA/HarvardOxford-cort-maxprob-thr0-2mm_resampled.nii.gz"
OUTDIR="/Users/acalvet/Documents/MVPA_FISAX/TFM_git/results/final_brainmask/2_SVM_results_stai/reliable_anatomy/cluster_anatomy"

mkdir -p $OUTDIR

# -------- CLUSTERIZAR --------
echo ">> Calculando clústeres..."
cluster \
  --in=$IMG \
  --thresh=$THR \
  --mm \
  --oindex=$OUTDIR/cluster_index.nii \
  > $OUTDIR/cluster_summary.txt

# Extraer índices de clúster
CLUSTERS=$(awk 'NR>1 {print $1}' $OUTDIR/cluster_summary.txt)

# -------- PROCESAR CADA CLÚSTER --------
for C in $CLUSTERS; do
  echo ">> Procesando clúster $C"

  # Extraer clúster
  fslmaths $OUTDIR/cluster_index.nii \
    -thr $C -uthr $C -bin \
    $OUTDIR/cluster_${C}.nii.gz

  # Tamaño del clúster
  SIZE=$(fslstats $OUTDIR/cluster_${C}.nii.gz -V | awk '{print $1}')

  # Ignorar clústeres ridículos
  # if [ "$SIZE" -lt 3 ]; then
  #  echo "   - Clúster $C ignorado (size=$SIZE)"
  #  continue
  #fi

  # Overlap con atlas
  fslstats \
    -K $ATLAS \
    $OUTDIR/cluster_${C}.nii.gz \
    -V \
    > $OUTDIR/cluster_${C}_regions.txt

done

echo ">> Hecho. Resultados en $OUTDIR/"
