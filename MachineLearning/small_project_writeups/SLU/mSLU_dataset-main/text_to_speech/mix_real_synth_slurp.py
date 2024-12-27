import argparse
import csv
import random
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "synth_dir",
        type=str
    )
    parser.add_argument(
        "real_dir",
        type=str
    )
    parser.add_argument(
        "out_dir",
        type=str
    )
    parser.add_argument(
        "synth_ratio",
        type=float
    )
    return parser.parse_args()


def read_data(path):
    res = []
    with open(path) as fp:
        for item in csv.DictReader(fp, delimiter=","):
            res.append(item)

    return res


def main(args):
    synth_dir = Path(args.synth_dir)
    real_dir = Path(args.real_dir)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    synth_ratio = args.synth_ratio
    print(f"Always use full real data; Use {synth_ratio} synthetic data.")

    # mix train with a ratio
    for split in ["train", "dev", "test"]:
        print(f"Processing {split}...")

        synth_path = synth_dir / f"{split}.csv"
        real_path = real_dir / f"{split}.csv"
        out_path = out_dir / f"{split}.csv"

        synth_data = read_data(synth_path)
        real_data = read_data(real_path)
        print(f"Read {len(synth_data)} synth; {len(real_data)} real.")

        if split == "train":
            synth_num = int(synth_ratio * len(synth_data))
            print(f"Will choose {synth_num} / {len(synth_data)}")
            synth_samples = random.sample(synth_data, k=synth_num)
            final_data = real_data + synth_samples
        else:
            final_data = real_data

        with open(out_path, mode="w") as fp:
            fp.write(f"intent_class" + "," + "audio_path" + "\n")
            for item in final_data:
                fp.write(
                    item["intent_class"] + "," + item["audio_path"] + "\n"
                )

    print(f"Done!")


if __name__ == "__main__":
    _args = parse_args()
    main(_args)
