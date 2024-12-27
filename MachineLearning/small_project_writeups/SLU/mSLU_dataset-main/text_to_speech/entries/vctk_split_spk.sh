#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/text_to_speech
#$ -V
#$ -N vctk
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/text_to_speech/logs/split_spk.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=1G,mem_free=1G,'hostname=b*'

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

conda activate xtts

python split_speaker.py \
  /export/b12/cmeng9/VCTK/speaker-info.txt \
  /export/b12/cmeng9/VCTK/wav16khz \
  /export/b12/cmeng9/mSLU_dataset/text_to_speech/output/xtts \
  --wav_id 023
