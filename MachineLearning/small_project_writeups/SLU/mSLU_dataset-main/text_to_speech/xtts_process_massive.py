# We do multilingual TTS with voice cloning.
# We run TTS for all MASSIVE text.
# For dev & test:
#   We synthesize each sample using all speakers.
# For train:
#   We randomly sample some speakers for each sample.
#
# Output format:
# out_dir/
#   train/
#       train.jsonl
#       wavs/
#           ${spk}_${id}.wav
#   dev/
#       wavs/
#   test/
#       wavs/

import argparse
import copy
import csv
import dataclasses
import json
import logging
import os
import random
from pathlib import Path
from typing import List, Dict, Optional

import tqdm
from TTS.api import TTS  # noqa

from text_to_speech.mms_process_massive import read_full_massive_jsonl

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger(Path(__file__).stem)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "massive_dir",
        type=str,
        help="dir of massive."
    )
    parser.add_argument(
        "lang",
        type=str,
    )
    parser.add_argument(
        "tts_lang",
        type=str
    )
    parser.add_argument(
        "spk_meta_dir",
        type=str,
    )
    parser.add_argument(
        "out_dir",
        type=str,
        help="output of audios."
    )
    parser.add_argument(
        "--train_sample_ratio",
        type=float,
        default=4 / 20
    )
    return parser.parse_args()


@dataclasses.dataclass
class SpeakerInfo:
    gender: str
    spk_id: str
    wav_path: str


def load_spk_meta(path) -> List[SpeakerInfo]:
    res = []
    with open(path) as fp:
        for item in csv.DictReader(fp, delimiter="\t"):
            res.append(SpeakerInfo(**item))
    return res


def split_massive_data(
        path
) -> Dict[str, List[dict]]:
    dataset = read_full_massive_jsonl(path)

    res = {
        "test": [],
        "train": [],
        "dev": []
    }
    for item in dataset:
        partition = item["partition"]
        res[partition].append(item)
    return res


def generate_audio(
        speakers: List[SpeakerInfo],
        data: List[dict],
        meta_out_path: Path,
        wav_out_dir: Path,
        tts,
        tts_lang: str,
        spk_sample_ratio: Optional[float] = None
):
    meta_out_path.parent.mkdir(parents=True, exist_ok=True)
    wav_out_dir.mkdir(exist_ok=True, parents=True)

    if spk_sample_ratio is None:
        n_spk = None
    else:
        n_spk = int(spk_sample_ratio * len(speakers))
        logger.info(f"n speakers: {n_spk} / {len(speakers)}")

    with open(meta_out_path, mode="w") as fp:
        for item in tqdm.tqdm(data):
            for spk in speakers if n_spk is None else random.sample(population=speakers, k=n_spk):
                wav_out_path = wav_out_dir / f"{spk.spk_id}_{item['id']}.wav"

                if not wav_out_path.exists():
                    tts.tts_to_file(
                        text=item["utt"],
                        speaker_wav=spk.wav_path,
                        language=tts_lang,
                        file_path=wav_out_path.as_posix(),
                        split_sentences=False
                    )

                new_item = copy.copy(item)
                new_item["xtts"] = {
                    "path": wav_out_path.as_posix(),
                    "spk_id": spk.spk_id
                }
                json.dump(new_item, fp)
                fp.write("\n")


def main(args):
    # inputs
    massive_dir = Path(args.massive_dir)
    lang = args.lang

    dataset = split_massive_data(massive_dir / f"{lang}.jsonl")

    spk_meta_dir = Path(args.spk_meta_dir)

    train_sample_ratio = args.train_sample_ratio

    # outputs
    out_dir = Path(args.out_dir) / lang
    out_dir.mkdir(parents=True, exist_ok=True)

    # model
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to("cuda:0")
    tts_lang = args.tts_lang

    for split in ["dev", "test", "train"]:
        logger.info(f"Processing {split}...")

        speakers = load_spk_meta(spk_meta_dir / (split + ".tsv"))
        subset = dataset[split]

        sub_out_dir = out_dir / split
        sub_out_dir.mkdir(exist_ok=True)

        generate_audio(
            speakers,
            subset,
            sub_out_dir / f"{split}.jsonl",
            sub_out_dir / "wavs",
            tts,
            tts_lang,
            spk_sample_ratio=train_sample_ratio if split == "train" else None
        )
    logger.info(f"Finished!")


if __name__ == "__main__":
    _args = parse_args()
    main(_args)
