#!/bin/bash

# Define las rutas principales
SOURCE_DIR="/Users/acalvet/Documents/MVPA_FISAX/contrasts"
DEST_DIR="/Users/acalvet/Documents/MVPA_FISAX/TFM_git/contrasts_brainmask"
MASK="/Users/acalvet/Documents/MVPA_FISAX/TFM_git/brainmask_canlab_bin_resampled.nii"

# Encuentra todas las imágenes con_0001.nii y copia a la nueva ubicación
find "$SOURCE_DIR" -type f -name "con_0002.nii" | while read -r FILE; do
    # Extrae el subdirectorio correspondiente
    RELATIVE_PATH=$(dirname "${FILE#$SOURCE_DIR/}")
    
    # Crea la ruta de destino
    DEST_PATH="$DEST_DIR/$RELATIVE_PATH"
    mkdir -p "$DEST_PATH"

    # Copia la imagen al destino
    cp "$FILE" "$DEST_PATH/"
    
    # Define la ruta del archivo copiado
    COPIED_FILE="$DEST_PATH/con_0002.nii"

    # Genera la imagen multiplicada
    OUTPUT_FILE="$DEST_PATH/con_0001_mask.nii"
    fslmaths "$COPIED_FILE" -mul "$MASK" "$OUTPUT_FILE"
    fslchfiletype NIFTI "$OUTPUT_FILE.gz" "$OUTPUT_FILE"

    echo "Procesado: $OUTPUT_FILE"
done
