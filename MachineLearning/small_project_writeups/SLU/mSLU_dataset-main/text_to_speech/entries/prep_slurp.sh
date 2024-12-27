#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/text_to_speech
#$ -V
#$ -N prep_slurp
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/text_to_speech/logs/prep_slurp.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=1G,mem_free=1G,'hostname=b*'

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

set -x
python prep_slurp_data.py \
  /export/b12/cmeng9/slurp/dataset/slurp \
  /export/b12/cmeng9/slurp/audio/slurp_real \
  /export/b12/cmeng9/mSLU_dataset/text_to_speech/output/xtts/massive/zh-CN/s2i_data/intent.dict \
  /export/b12/cmeng9/slurp/dataset/slurp_s2i
