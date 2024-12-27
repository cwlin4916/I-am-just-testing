# The source audios would come from VCTK.
# We need to:
#   1. Decide which source speakers to use. (train, dev, test)
#   2. Decide which source audios to use for each speaker. (the longest for now.)
# Input:
#   speaker-info.txt
#   audio dir: stores all the audios
# Output:
#   out_dir/
#       train.tsv
#       dev.tsv
#       test.tsv
#   where each file contains
#       speaker_id  /path/to/wav
#   indicating which wav file to use for that speaker.
import argparse
import dataclasses
import glob
import logging
import os
from pathlib import Path
from typing import List, Union, Optional

import soundfile

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger(Path(__file__).stem)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "speaker_info_path",
        type=str,
    )
    parser.add_argument(
        "wav_dir",
        type=str,
    )
    parser.add_argument(
        "out_dir",
        type=str
    )
    parser.add_argument(
        "--wav_id",
        default=None,
        type=str,
    )
    parser.add_argument(
        "--n_dev_test",
        type=int,
        default=2,
        help="num of M/F speakers for dev and test sets."
    )
    parser.add_argument(
        "--n_train",
        type=int,
        default=10,
        help="num of M/F speakers for train set. <=0 means all the rest."
    )
    return parser.parse_args()


@dataclasses.dataclass
class SpeakerInfo:
    gender: str
    spk_id: str


def choose_wav(speakers: List[SpeakerInfo], wav_dir: Path, wav_id: Optional[str] = None) -> List[str]:
    res = []
    for spk in speakers:
        if wav_id is not None:
            wav_path = wav_dir / spk.spk_id / f"{spk.spk_id}_{wav_id}_mic1.wav"
            assert wav_path.exists(), wav_path.as_posix()
            res.append(wav_path.as_posix())
        else:
            all_audios = glob.glob(
                (wav_dir / spk.spk_id / "*.wav").as_posix()
            )
            all_durs = [
                (soundfile.info(_path).frames / 16000, _path)
                for _path in all_audios
            ]
            all_durs.sort(key=lambda x: -x[0])

            res.append(all_durs[0][1])

            logger.info(all_durs[0])

    return res


def write_to_output(
        speakers: List[SpeakerInfo],
        wavs: List[str],
        out_path: Union[str, Path]
):
    assert len(speakers) == len(wavs)
    with open(out_path, mode="w") as fp:
        # header
        fp.write("spk_id" + "\t" + "gender" + "\t" + "wav_path" + "\n")
        for spk, wav in zip(speakers, wavs):
            fp.write(spk.spk_id + "\t" + spk.gender + "\t" + wav + "\n")


def main(args):
    speaker_info_path = args.speaker_info_path
    wav_dir = Path(args.wav_dir)
    wav_id = args.wav_id

    n_dev_test = args.n_dev_test
    n_train = args.n_train

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # group by male and female
    male_speakers = []
    female_speakers = []
    with open(speaker_info_path) as fp:
        fp.readline()
        for line in fp:
            line = line.strip().split()
            gender = line[2]
            assert gender in ["M", "F"]
            spk_id = line[0]

            if gender == "F":
                female_speakers.append(
                    SpeakerInfo(
                        gender=gender,
                        spk_id=spk_id
                    )
                )
            else:
                male_speakers.append(
                    SpeakerInfo(
                        gender=gender,
                        spk_id=spk_id
                    )
                )
    logger.info(f"{len(female_speakers)} F | {len(male_speakers)} M")

    # test: 5M + 5F
    test_speakers = male_speakers[:n_dev_test] + female_speakers[:n_dev_test]
    # dev: 5M + 5F
    dev_speakers = male_speakers[n_dev_test:2 * n_dev_test] + female_speakers[n_dev_test:2 * n_dev_test]
    # train: the rest
    if n_train <= 0:
        train_speakers = male_speakers[2 * n_dev_test:] + female_speakers[2 * n_dev_test:]
    else:
        train_speakers = male_speakers[2 * n_dev_test:2 * n_dev_test + n_train] + \
                         female_speakers[2 * n_dev_test:2 * n_dev_test + n_train]
    assert len(
        set([_spk.spk_id for _spk in test_speakers]) & set([_spk.spk_id for _spk in dev_speakers]) & \
        set([_spk.spk_id for _spk in train_speakers])
    ) == 0

    logger.info(
        f"n test: {len(test_speakers)} | n dev: {len(dev_speakers)} | n train: {len(train_speakers)}"
    )

    test_wavs = choose_wav(test_speakers, wav_dir, wav_id=wav_id)
    dev_wavs = choose_wav(dev_speakers, wav_dir, wav_id=wav_id)
    train_wavs = choose_wav(train_speakers, wav_dir, wav_id=wav_id)

    write_to_output(test_speakers, test_wavs, out_path=out_dir / "test.tsv")
    write_to_output(dev_speakers, dev_wavs, out_path=out_dir / "dev.tsv")
    write_to_output(train_speakers, train_wavs, out_path=out_dir / "train.tsv")


if __name__ == "__main__":
    _args = parse_args()
    main(_args)
