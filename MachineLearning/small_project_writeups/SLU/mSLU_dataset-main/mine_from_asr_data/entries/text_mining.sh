#!/usr/bin/bash

#$ -wd /export/b12/cmeng9/speech_vecalign
#$ -V
#$ -N massive_cv_mine
#$ -j y -o /export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/logs/massive_cv_mine.log
#$ -M cmeng9@jhu.edu
#$ -m e
#$ -l ram_free=8G,mem_free=8G,gpu=1,'hostname=c1*|c0[12345689]*'
# Submit to GPU queue
#$ -q g.q

# Assign a free-GPU to your program (make sure -n matches the requested number of GPUs above)
set -e

source /home/gqin2/scripts/acquire-gpu

conda activate laser

lang=en

cv_index_type="OPQ64,IVF4096,PQ64"
massive_index_type="Flat"

commonvoice_dir=/export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/commonvoice
massive_dir=/export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/massive
out_dir=/export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/output/text_mining/massive_cv

set -x
python -m voxpopuli_example.global_mining.global_mine \
  --src_index ${commonvoice_dir}/${lang}/index/populate_index.idx \
  --tgt_index ${massive_dir}/${lang}/index/populate_index.idx \
  --src_index_type ${cv_index_type} --tgt_index_type ${massive_index_type} \
  --src_query_embeddings "${commonvoice_dir}/${lang}/shard.*.embed" \
  --tgt_query_embeddings "${massive_dir}/${lang}/shard.*.embed" \
  --src_text_files "${commonvoice_dir}/${lang}/shard.*.txt" \
  --tgt_text_files "${massive_dir}/${lang}/shard.*.txt" \
  --out_dir ${out_dir}/${lang}/text

python -m voxpopuli_example.global_mining.global_mine \
  --src_index ${commonvoice_dir}/${lang}/index/populate_index.idx \
  --tgt_index ${massive_dir}/${lang}/index/populate_index.idx \
  --src_index_type ${cv_index_type} --tgt_index_type ${massive_index_type} \
  --src_query_embeddings "${commonvoice_dir}/${lang}/shard.*.embed" \
  --tgt_query_embeddings "${massive_dir}/${lang}/shard.*.embed" \
  --src_text_files "${commonvoice_dir}/${lang}/shard.*.meta" \
  --tgt_text_files "${massive_dir}/${lang}/shard.*.meta" \
  --out_dir ${out_dir}/${lang}/meta
set +x
