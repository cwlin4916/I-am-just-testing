#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data
#$ -V
#$ -N embed_en
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/logs/embed_en.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=6G,mem_free=6G,gpu=1,'hostname=c1*|c0[12345689]*'
# Submit to GPU queue
#$ -q g.q

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

source /home/gqin2/scripts/acquire-gpu

conda activate laser

set -x
# MASSIVE
python laser2_embed.py \
  /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/massive/en/shard.0.txt \
  /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/massive/en/shard.0.embed

# COMMONVOICE
python laser2_embed.py \
  /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/commonvoice/en/shard.0.txt \
  /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/commonvoice/en/shard.0.embed
