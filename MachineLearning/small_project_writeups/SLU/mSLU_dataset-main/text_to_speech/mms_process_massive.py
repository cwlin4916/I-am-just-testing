import argparse
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional

import soundfile
import torch
import tqdm
from transformers import VitsTokenizer, VitsModel, set_seed  # noqa

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
        "out_dir",
        type=str,
        help="output of audios."
    )
    return parser.parse_args()


def read_full_massive_jsonl(path) -> List[dict]:
    res = []
    with open(path) as fp:
        for line in fp:
            utt = json.loads(line.strip())
            res.append(utt)
    return res


def generate_audio(model_name: str, text: str, output_wav_path: str, seed: int = 42):
    """Input: model_name (str), text (str), output_wav_path (str), seed (int)
    Output: audio from the text and saves it as WAV file at output_wav_path"""
    tokenizer = VitsTokenizer.from_pretrained(model_name)
    model = VitsModel.from_pretrained(model_name)
    inputs = tokenizer(text=text, return_tensors="pt")
    set_seed(seed)
    with torch.no_grad():
        outputs = model(**inputs)
    waveform = outputs.waveform[0].numpy()
    soundfile.write(output_wav_path, samplerate=model.config.sampling_rate, data=waveform)


def process_massive_single_language(
        lang: str, model_name: str,
        massive_meta: Path,
        out_dir: Path,
        num_instances: Optional[int] = None
):
    out_dir.mkdir(parents=True, exist_ok=True)
    wav_dir = out_dir / "wavs"
    wav_dir.mkdir(exist_ok=True)
    # Load the dataset
    dataset = read_full_massive_jsonl(massive_meta)

    # Determine the range based on num_instances
    instances_to_process = dataset if (num_instances is None or num_instances <= 0) else dataset[:num_instances]
    output_meta = []
    out_meta_path = out_dir / f"{lang}.jsonl"
    if out_meta_path.exists():
        logger.info(f"{out_meta_path} exists! Will skip.")
        return

    for ii, instance in enumerate(tqdm.tqdm(instances_to_process)):
        instance = dataset[ii]

        text = instance["utt"]
        audio_path = wav_dir / f"{ii}.wav"
        generate_audio(model_name, text, audio_path.as_posix())

        assert "syn_audio" not in instance
        instance["syn_audio"] = {
            "path": audio_path.as_posix()
        }
        output_meta.append(instance)

    with open(out_dir / f"{lang}.jsonl", mode="w") as fp:
        for item in output_meta:
            json.dump(item, fp)
            fp.write("\n")


# A version which inputs a model map for multiple languages
def process_massive(
        languages: List[str], model_map: Dict[str, str], massive_dir: Path,
        out_dir: Path,
        num_instances: Optional[int] = None

):
    for lang in languages:
        model_name = model_map[lang]
        process_massive_single_language(
            lang, model_name,
            massive_dir / f"{lang}.jsonl",
            out_dir / lang,
            num_instances
        )


def main(args):
    # inputs
    languages = ["en-US", "de-DE", "vi-VN"]
    massive_dir = Path(args.massive_dir)
    with open("mms_model_map.json") as fp:
        model_map = json.load(fp)
    for _lang in languages:
        assert _lang in model_map, f"{_lang} does not have a corresponding model!"

    # outputs
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # to create the actual model_map, we will need to run the create_model_map.py script
    # this creates an INCOMPLETE model_map, some languages are missing because that for MASSIVE does not match TTS iso coding.
    # To process all instances, pass num_instances=None
    process_massive(
        languages, model_map, massive_dir, out_dir
    )


if __name__ == "__main__":
    _args = parse_args()
    main(_args)
