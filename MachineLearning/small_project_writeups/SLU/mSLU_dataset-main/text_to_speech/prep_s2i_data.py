# this script prepares speech to intent data.
import argparse
import json
from pathlib import Path
from typing import List, Dict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_dir",
        type=str,
    )
    parser.add_argument(
        "out_dir",
        type=str
    )
    return parser.parse_args()


def load_json_line(line: str):
    try:
        data = json.loads(line.strip())
        return data
    except json.decoder.JSONDecodeError as e:
        print(f"{e}")
        print(f"Error line: {line.strip()}")
        return None


def convert(
        in_jsonl,
        intent_dict: Dict[str, int],
        out_csv
):
    with open(in_jsonl) as in_fp, \
            open(out_csv, mode="w") as out_fp:
        # header
        out_fp.write(f"intent_class" + "," + "audio_path" + "\n")

        for line in in_fp:
            data = load_json_line(line)
            if data is None:
                continue
            intent_id = intent_dict[data["intent"]]
            audio_path = data["xtts"]["path"]
            out_fp.write(f"{intent_id}" + "," + audio_path + "\n")


def read_all_intents(path) -> List[str]:
    res = set()
    with open(path) as fp:
        for line in fp:
            data = load_json_line(line)
            if data is None:
                continue
            intent = data["intent"]
            res.add(intent)
    return sorted(list(res))


def main(args):
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # get intent 2 id from train
    intents = read_all_intents(in_dir / "train" / f"train.jsonl")
    intent_dict = {
        _intent: _id for _id, _intent in enumerate(intents)
    }
    with open(out_dir / f"intent.dict", mode="w") as fp:
        for _intent in intents:
            fp.write(_intent + " " + str(intent_dict[_intent]) + "\n")
    print(f"Got {len(intents)} intents.")

    # write all splits
    for split in ["train", "dev", "test"]:
        in_json = in_dir / split / f"{split}.jsonl"
        out_csv = out_dir / f"{split}.csv"
        convert(in_json, intent_dict, out_csv)


if __name__ == "__main__":
    _args = parse_args()
    main(_args)
