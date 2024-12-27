import argparse
import gzip
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_path",
        type=str
    )
    parser.add_argument(
        "out_path",
        type=str
    )
    parser.add_argument(
        "intent_dict",
        type=str
    )
    parser.add_argument(
        "--th_score",
        type=float,
        default=1.09
    )
    return parser.parse_args()


def main(args):
    th_score = args.th_score

    intent_dict = {}
    with open(args.intent_dict) as fp:
        for line in fp:
            intent, intent_id = line.strip().split(" ")
            intent_dict[intent] = intent_id

    out_path = Path(args.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with gzip.open(args.in_path, mode="rt") as in_fp, \
            open(out_path, mode="w") as out_fp:
        out_fp.write(f"intent_class" + "," + "audio_path" + "\n")

        for line in in_fp:
            score, aud_path, intent = line.strip().split("\t")
            score = float(score)
            if score < th_score:
                break

            out_fp.write(f"{intent_dict[intent]}" + "," + aud_path + "\n")


if __name__ == '__main__':
    _args = parse_args()
    main(_args)
