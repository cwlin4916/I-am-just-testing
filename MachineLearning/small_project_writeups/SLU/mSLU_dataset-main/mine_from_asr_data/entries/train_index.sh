#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/speech_vecalign
#$ -V
#$ -N train_index
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/logs/index_en.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=8G,mem_free=8G,gpu=1,'hostname=c1*|c0[12345689]*'
# Submit to GPU queue
#$ -q g.q

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

source /home/gqin2/scripts/acquire-gpu

conda activate laser

echo "MASSIVE"

set -x
python -m voxpopuli_example.global_mining.train_index \
  --data_dir /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/massive/en \
  --tmp_dir /export/b12/cmeng9/tmp \
  --out_dir /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/massive/en/index \
  --fp16 \
  --sample_size -1 \
  --index_type Flat
set +x

echo "CommonVoice"

set -x
python -m voxpopuli_example.global_mining.train_index \
  --data_dir /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/commonvoice/en \
  --tmp_dir /export/b12/cmeng9/tmp \
  --out_dir /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/commonvoice/en/index \
  --fp16 \
  --sample_size -1
set +x
