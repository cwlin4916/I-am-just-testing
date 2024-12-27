#!/usr/bin/bash

#SBATCH --job-name=ffmpeg      ### Name of the Job
#SBATCH --output=/export/b12/cmeng9/mSLU_dataset/mine_from_asr_data/logs/cv_convert.log
#SBATCH --partition=cpu         ### Name of the queue
#SBATCH --nodes=1                ### Number of nodes requested
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --cpus-per-task=16        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=1G         ### Define memory per core. The default is set to 1 GB. This   should  NOT be set for the parallel queue
#SBATCH --mail-type=end          # send email when job ends
#SBATCH --mail-type=fail         # send email if job fails
#SBATCH --mail-user=cmeng9@jhu.edu

set -e

module purge
module load conda
module load ffmpeg
export PATH="/home/cmeng9/miniconda3/envs/ffmpeg/bin:$PATH"
source activate /home/cmeng9/miniconda3/envs/ffmpeg

set -x
python -m mine_from_asr_data.cv_convert
