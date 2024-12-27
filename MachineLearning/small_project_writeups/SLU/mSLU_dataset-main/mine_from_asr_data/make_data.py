# here, we only prepare `shard.{shard_id}.nl` and `shard.{shard_id}.meta` files.
# you need to deal with the `shard.{shard_id}.embed` yourself.
# now they only have one shard, as they are pretty small.
import argparse
import logging
import os
from pathlib import Path

from metadata_read_utils import read_router

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
        "metadata_type",
        type=str,
        help="which type of reader is needed."
    )
    parser.add_argument(
        "out_dir",
        type=str,
        help="out dir to store the metas."
    )
    return parser.parse_args()


def main(args):
    metadata, metadata_type = args.metadata, args.metadata_type
    logger.info(f"Read {metadata} as {metadata_type}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_text_path = out_dir / f"shard.0.txt"
    out_nl_path = out_dir / f"shard.0.nl"

    lines = read_router(metadata, metadata_type)

    with open(out_nl_path, mode="w") as fp:
        fp.write(f"{len(lines)}\n")

    with open(out_text_path, mode="w") as fp:
        for line in lines:
            fp.write(line + "\n")

    logger.info("Finished!")


if __name__ == '__main__':
    _args = parse_args()
    main(_args)
