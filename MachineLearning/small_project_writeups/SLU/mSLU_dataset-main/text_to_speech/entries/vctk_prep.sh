#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/text_to_speech
#$ -V
#$ -N vctk
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/text_to_speech/logs/vctk.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=2G,mem_free=2G,'hostname=b*'

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

python vctk_prep.py \
  /export/b12/cmeng9/VCTK/wav48_silence_trimmed \
  /export/b12/cmeng9/VCTK/wav16khz
