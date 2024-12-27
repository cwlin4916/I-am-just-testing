#!/bin/bash -l
#SBATCH --job-name=tts      ### Name of the Job
#SBATCH --output=/export/b12/cmeng9/mSLU_dataset/text_to_speech/logs/xtts.en.log
#SBATCH --partition=gpu         ### Name of the queue
#SBATCH --nodes=1                ### Number of nodes requested
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --cpus-per-task=2        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=4G         ### Define memory per core. The default is set to 1 GB. This   should  NOT be set for the parallel queue
#SBATCH --gres=gpu:1             ### Number of GPUs per node
#SBATCH --mail-type=end          # send email when job ends
#SBATCH --mail-type=fail         # send email if job fails
#SBATCH --mail-user=cmeng9@jhu.edu

set -e

module load conda
export PATH="/home/cmeng9/miniconda3/envs/xtts/bin:$PATH"
source activate /home/cmeng9/miniconda3/envs/xtts

set -x

python -m text_to_speech.xtts_process_massive \
    /export/b12/cmeng9/massive/1.1/data \
    en-US \
    en \
    /export/b12/cmeng9/mSLU_dataset/text_to_speech/output/xtts \
    /export/b12/cmeng9/mSLU_dataset/text_to_speech/output/xtts/massive
