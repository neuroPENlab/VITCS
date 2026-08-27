import gl
from os.path import join

# IMPORTANT: before running this script, run figsup06d_1_reliable_anatomy_VITCS_late_PREPROC.sh
# RUN THIS SCRIPT IN MRIcroGL

basedir = '<PATH_TO_PROJECT>' # <-- EDIT THIS
outputdir = join(basedir, 'results', 'VITCS_late_results', 'reliable_anatomy')
figdir = join(basedir, 'figures')

gl.resetdefaults()
gl.loadimage('spm152')
gl.backcolor(255, 255, 255)

# UNC 0.01 POSITIVE
gl.overlayload(join(outputdir, 'UNC01_pruned001_pos.nii.gz'))
gl.colorname(1,"8redyell")
gl.minmax(1, 0.9, 2)

# UNC 0.01 NEGATIVE
gl.overlayload(join(outputdir, 'UNC01_pruned001_neg.nii.gz'))
gl.colorname(2,"electric_blue")
gl.minmax(2, 0.8, 2)

# UNC 0.001 POSITIVE
gl.overlayload(join(outputdir, 'VITCS_bootstrap_unc001_pos_bin.nii.gz'))
gl.colorname(3,"8redyell")
gl.minmax(3, 0, 1.8)

# UNC 0.001 NEGATIVE
gl.overlayload(join(outputdir, 'VITCS_bootstrap_unc001_neg_bin.nii.gz'))
gl.colorname(4,"electric_blue")
gl.minmax(4, 0, 2.2)

gl.colorbarposition(0)

gl.mosaic("A H 0.08 V 0.08 39 27 -5 S H 0.08 V 0.08 -35 20 51 C H 0.08 V 0.08 -29 -62")

gl.savebmp(join(figdir, 'sup_fig6d_VITCS_late.png'))