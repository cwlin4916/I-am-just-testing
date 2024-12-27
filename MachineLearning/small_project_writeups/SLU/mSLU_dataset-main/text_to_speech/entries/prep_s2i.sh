#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/text_to_speech
#$ -V
#$ -N prep_s2i
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/text_to_speech/logs/prep_s2i.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=1G,mem_free=1G,'hostname=b*'

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

python prep_s2i_data.py \
  /export/b12/cmeng9/mSLU_dataset/text_to_speech/output/xtts/massive/en-US/ \
  /export/b12/cmeng9/mSLU_dataset/text_to_speech/output/xtts/massive/en-US/s2i_data
