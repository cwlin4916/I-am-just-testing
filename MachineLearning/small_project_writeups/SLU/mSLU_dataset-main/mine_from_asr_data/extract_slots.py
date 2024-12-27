import argparse
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger(Path(__file__).stem)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in_file",
        required=True,
        type=str,
        help="the input file. should be .jsonl."
    )
    parser.add_argument(
        "--out_file",
        required=True,
        type=str,
        help="the output file."
    )
    return parser.parse_args()


def main(args):
    out_file = Path(args.out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    phrase2label: Dict[str, str] = {}
    banned_phrases = set()

    n_tot = n_skip = 0
    with open(args.in_file) as fp:
        for line in fp:
            n_tot += 1
            annot_utt = json.loads(line.strip())["annot_utt"]
            # e.g., [('time', '兩小時後')]
            annotations: List[Tuple[str, str]] = re.findall(
                pattern=r'\[(\S+) : ([^\[]+)\]',
                string=annot_utt
            )

            if len(annotations) == 0:
                n_skip += 1
                continue
            else:
                # e.g., label=time, phrase=兩小時後
                for label, phrase in annotations:
                    if phrase in banned_phrases:
                        continue
                    # expect one phrase has the same type
                    if phrase in phrase2label:
                        if label != phrase2label[phrase]:
                            logger.info(f"{phrase} has ambiguous labels: {label} and {phrase2label[phrase]}. "
                                        f"Drop this phrase.")
                            banned_phrases.add(phrase)
                    else:
                        phrase2label[phrase] = label

    logger.info(f"Total {n_tot} lines; {n_skip} does not have valid slots.")
    logger.info(f"Found {len(phrase2label)} phrases.")

    # write in the format of: phrase\tlabel
    with open(out_file, "w") as fp:
        for phrase in sorted(list(phrase2label.keys())):
            if phrase in banned_phrases:
                continue
            fp.write(f"{phrase}\t{phrase2label[phrase]}\n")

    logger.info(f"Done.")


if __name__ == '__main__':
    _args = parse_args()
    main(_args)
