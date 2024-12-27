#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/text_to_speech
#$ -V
#$ -N mix
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/text_to_speech/logs/mix_real_synth_slurp.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=1G,mem_free=1G,'hostname=b*'

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

for ratio in 0.2 0.4 0.6 0.8
do
  set -x
  python mix_real_synth_slurp.py \
      /export/b12/cmeng9/mSLU_dataset/text_to_speech/output/xtts/massive/en-US/s2i_data \
      /export/b12/cmeng9/slurp/dataset/slurp_headset_s2i \
      /export/b12/cmeng9/mSLU_dataset/text_to_speech/output/slurp_ablate/real_${ratio}synth/ \
      ${ratio}
  set +x
done
