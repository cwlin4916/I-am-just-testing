import argparse
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List

import tqdm

from metadata_read_utils import read_vox_tsv, read_commonvoice_tsv, read_router
from mp_utils import start_multi_processes

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger(Path(__file__).stem)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "slot_tsv",
        type=str,
        help="the path of the slot."
    )
    parser.add_argument(
        "asr_tsv",
        type=str,
        help="currently for voxpopuli only."
    )
    parser.add_argument(
        "asr_type",
        type=str,
        help="the name of the asr dataset."
    )
    parser.add_argument(
        "out_path",
        type=str,
        help="the output path."
    )
    parser.add_argument(
        "--n_proc",
        type=int,
        default=24,
    )
    return parser.parse_args()


def load_slots(path) -> Dict[str, str]:
    res = {}
    with open(path) as fp:
        for line in fp:
            phrase, label = line.strip().split("\t")
            res[phrase] = label

    return res


def find_phrases(
        text: str,
        all_phrases: List[str]
) -> List[re.Match]:
    all_matches = []
    for phrase in all_phrases:
        matches = list(re.finditer(rf"\b{phrase}\b", text))
        if len(matches) == 0:
            continue
        all_matches.extend(matches)

    return all_matches


def annotate_text(
        text: str,
        all_matches: List[re.Match],
        phrase_to_slot_type: Dict[str, str]
) -> str:
    annot_text = text[:all_matches[0].start()]
    for ii in range(len(all_matches) - 1):
        match = all_matches[ii]
        next_match = all_matches[ii + 1]
        matched_phrase = text[match.start():match.end()]
        annot_text = f"{annot_text}[{matched_phrase} : {phrase_to_slot_type[matched_phrase]}]{text[match.end():next_match.start()]}"
    last_match = all_matches[-1]
    matched_phrase = text[last_match.start():last_match.end()]
    annot_text = f"{annot_text}[{matched_phrase} : {phrase_to_slot_type[matched_phrase]}]{text[last_match.end():]}"

    return annot_text


def clean_spans(spans: List[re.Match]) -> List[re.Match]:
    # 0 or 1
    if len(spans) < 2:
        return spans

    # if start is the same, the one covers more will be first
    spans.sort(key=lambda x: (x.start(), -(x.end() - x.start())))

    res = [spans[0]]
    for ii in range(1, len(spans)):
        this_span = spans[ii]
        prev_span = res[-1]
        # if starts the same
        if this_span.start() == prev_span.start():
            continue
        # if starts earlier than the prev's end
        if this_span.start() < prev_span.end():
            continue

        res.append(this_span)
    return res


def run(
        pid: int,
        vox_lines: List[str],
        all_phrases: List[str],
        phrase_to_slot_type: Dict[str, str],
        out_dir: Path
):
    with open(out_dir / f"{pid}.txt", mode="w") as out_fp:
        for text in tqdm.tqdm(vox_lines, desc=f"[Proc {pid}]"):

            all_match_spans = find_phrases(text, all_phrases)
            all_match_spans = clean_spans(all_match_spans)
            if len(all_match_spans) == 0:
                continue

            annot_text = annotate_text(text, all_match_spans, phrase_to_slot_type)
            out_fp.write(annot_text + "\n")


def main(args):
    out_path = Path(args.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    phrase_to_slot_type = load_slots(args.slot_tsv)
    all_phrases = list(phrase_to_slot_type.keys())

    asr_type = args.asr_type
    asr_tsv = args.asr_tsv
    logger.info(f"ASR args: type={asr_type} | tsv={asr_tsv}")

    asr_lines = read_router(asr_tsv, asr_type)
    n_proc = args.n_proc

    with tempfile.TemporaryDirectory() as _tmp_dir:
        tmp_dir = Path(_tmp_dir)
        start_multi_processes(
            data=asr_lines,
            n_proc=n_proc,
            func=run,
            all_phrases=all_phrases,
            phrase_to_slot_type=phrase_to_slot_type,
            out_dir=tmp_dir
        )

        with open(out_path, mode="w") as out_fp:
            for ii in range(n_proc):
                with open(tmp_dir / f"{ii}.txt") as in_fp:
                    for line in in_fp:
                        out_fp.write(line)
    logger.info("Finished!")


if __name__ == '__main__':
    _args = parse_args()
    main(_args)
