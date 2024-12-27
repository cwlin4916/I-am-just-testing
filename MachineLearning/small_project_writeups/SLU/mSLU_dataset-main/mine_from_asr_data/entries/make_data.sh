#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data
#$ -V
#$ -N make_data
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/logs/make_data.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=2G,mem_free=2G,'hostname=b*'
# Submit to GPU queue
#$ -q g.q

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e
set -x

python make_cv_data.py \
  /export/corpora5/CommonVoice/en_1488h_2019-12-10/train.tsv \
  /export/b12/cmeng9/CommonVoice/en_1488h_2019-12-10/clips \
  /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/commonvoice/en

python make_massive_data.py \
  /export/b12/cmeng9/massive/1.1/data/en-US.jsonl \
  /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/massive/en
