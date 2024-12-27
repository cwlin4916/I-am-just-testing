# here, we only prepare `shard.{shard_id}.nl` and `shard.{shard_id}.meta` files.
# you need to deal with the `shard.{shard_id}.embed` yourself.
# now they only have one shard, as they are pretty small.
import argparse
import dataclasses
import json
import logging
import os
from pathlib import Path

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger(Path(__file__).stem)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "metadata",
        type=str,
        help="the input meta data containing text."
    )
    parser.add_argument(
        "out_dir",
        type=str,
        help="out dir to store the metas."
    )
    return parser.parse_args()


@dataclasses.dataclass
class MassiveMeta:
    sentence: str
    intent: str


def main(args):
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_text_path = out_dir / f"shard.0.txt"
    out_nl_path = out_dir / f"shard.0.nl"
    out_meta_path = out_dir / f"shard.0.meta"

    all_metas = []
    with open(args.metadata) as fp:
        for line in fp:
            item = json.loads(line.strip())
            all_metas.append(
                MassiveMeta(
                    sentence=item["utt"],
                    intent=item["intent"]
                )
            )

    with open(out_nl_path, mode="w") as fp:
        fp.write(f"{len(all_metas)}\n")

    with open(out_text_path, mode="w") as fp:
        for item in all_metas:
            fp.write(item.sentence + "\n")

    with open(out_meta_path, mode="w") as fp:
        for item in all_metas:
            fp.write(item.intent + "\n")

    logger.info("Finished!")


if __name__ == '__main__':
    _args = parse_args()
    main(_args)
