#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/text_to_speech
#$ -V
#$ -N mms
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/text_to_speech/logs/mms.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=8G,mem_free=8G,gpu=1,'hostname=c1*|c0[12345689]*'
# Submit to GPU queue
#$ -q g.q

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

source /home/gqin2/scripts/acquire-gpu

conda activate tts

python mms_process_massive.py \
  /export/b12/cmeng9/massive/1.1/data \
  /export/b12/cmeng9/mSLU_dataset/text_to_speech/output
