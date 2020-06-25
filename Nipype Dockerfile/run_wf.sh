#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/fsl/5.0
export PATH=/opt/miniconda-latest/envs/neuro/bin:/opt/miniconda-latest/condabin:/usr/lib/fsl/5.0:/opt/miniconda-latest/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export FORCE_SPMMCR=1
export FSLBROWSER=/etc/alternatives/x-www-browser
export FSLDIR=/usr/share/fsl/5.0
export FSLLOCKDIR=
export FSLMACHINELIST=
export FSLMULTIFILEQUIT=TRUE
export FSLOUTPUTTYPE=NIFTI_GZ
export FSLREMOTECALL=
export FSLTCLSH=/usr/bin/tclsh
export FSLWISH=/usr/bin/wish
export MATLABCMD=/opt/matlabmcr-2010a/v713/toolbox/matlab
export SPMMCRCMD='/opt/spm12-dev/run_spm12.sh /opt/matlabmcr-2010a/v713 script'
source activate neuro
python download_data.py $DATA
python download_script.py $SCRIPT
A="$(cut -d'/' -f2 <<<$SCRIPT)"
python "/script/${A}.py"
python write_output_files.py