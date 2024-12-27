#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data
#$ -V
#$ -N search_text
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/logs/search_text.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=4G,mem_free=4G,'hostname=b*'

set -e
set -x

python search_from_text.py \
  /export/b12/cmeng9/massive/slots/en-US.tsv \
  /export/corpora5/voxpopuli/transcribed_data/en/asr_train.tsv \
  voxpopuli \
  /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/vox_train.en

python search_from_text.py \
  /export/b12/cmeng9/massive/slots/en-US.tsv \
  /export/corpora5/CommonVoice/en_1488h_2019-12-10/train.tsv \
  commonvoice \
  /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/commonvoice_train.en
