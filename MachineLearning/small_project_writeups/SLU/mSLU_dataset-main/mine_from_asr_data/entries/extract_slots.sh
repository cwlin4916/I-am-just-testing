#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data
#$ -V
#$ -N extract_slots
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/logs/extract_slots.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=4G,mem_free=4G,'hostname=b*'

set -e
set -x

python extract_slots.py \
  --in_file /export/b12/cmeng9/massive/1.1/data/en-US.jsonl \
  --out_file /export/b12/cmeng9/massive/slots/en-US.tsv
