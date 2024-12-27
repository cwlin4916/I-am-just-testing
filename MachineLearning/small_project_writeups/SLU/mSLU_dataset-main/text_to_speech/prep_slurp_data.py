import argparse
import json
from pathlib import Path
from typing import Dict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_dir",
        type=str,
    )
    parser.add_argument(
        "audio_dir",
        type=str
    )
    parser.add_argument(
        "intent_dict",
        type=str,
    )
    parser.add_argument(
        "out_dir",
        type=str
    )
    return parser.parse_args()


def load_intent_dict(path) -> Dict[str, int]:
    res = {}
    with open(path) as fp:
        for line in fp:
            k, v = line.strip().split(" ")
            assert k not in res
            res[k] = v
    return res


def convert(
        in_jsonl,
        audio_dir: Path,
        intent_dict: Dict[str, int],
        out_csv,
        out_headset_csv
):
    miss_cnt = 0
    with open(in_jsonl) as in_fp, \
            open(out_csv, mode="w") as out_fp, \
            open(out_headset_csv, mode="w") as out_headset_fp:
        # header
        out_fp.write(f"intent_class" + "," + "audio_path" + "\n")
        out_headset_fp.write(f"intent_class" + "," + "audio_path" + "\n")

        for line in in_fp:
            data = json.loads(line.strip())
            if data["intent"] not in intent_dict:
                miss_cnt += 1
                continue
            else:
                intent_id = intent_dict[data["intent"]]
            recordings = data["recordings"]
            for rec in recordings:
                filename = rec["file"]
                aud_path = audio_dir / filename
                if "headset" in filename:
                    out_headset_fp.write(f"{intent_id}" + "," + aud_path.as_posix() + "\n")
                else:
                    out_fp.write(f"{intent_id}" + "," + aud_path.as_posix() + "\n")
    print(f"{miss_cnt} lines skipped for {in_jsonl}")


def main(args):
    in_dir = Path(args.in_dir)
    audio_dir = Path(args.audio_dir)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    intent_dict = load_intent_dict(args.intent_dict)

    for split in ["train", "dev", "test"]:
        convert(
            in_dir / f"{split}.jsonl",
            audio_dir,
            intent_dict,
            out_dir / f"{split}.csv",
            out_dir / f"{split}.headset.csv"
        )


if __name__ == "__main__":
    _args = parse_args()
    main(_args)
