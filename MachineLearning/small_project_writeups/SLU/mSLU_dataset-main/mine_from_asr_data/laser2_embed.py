import argparse
import logging
import os
from pathlib import Path

import tqdm
from laser_encoders import LaserEncoderPipeline  # noqa
from stopes.utils.embedding_utils import EmbeddingConcatenator  # noqa

from metadata_read_utils import read_lines

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger(Path(__file__).stem)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "sent_in_path",
        type=str,
        help="the path containing all sentences."
    )
    parser.add_argument(
        "out_path",
        type=str,
        help="the output embedding path."
    )
    parser.add_argument(
        "--model_dir",
        type=str,
        default="/export/b12/cmeng9/LASER/nllb"
    )
    parser.add_argument(
        "--bsz",
        type=str,
        default=1024,
        help="number of sentences embedded at a time."
    )
    return parser.parse_args()


def main(args):
    bsz = args.bsz
    lines = read_lines(args.sent_in_path)
    n_batches = len(lines) // bsz
    if len(lines) % bsz != 0:
        n_batches += 1

    logger.info(f"Total # sent: {len(lines)} | bsz: {bsz} | n_batches: {n_batches}")

    out_path = Path(args.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        logger.warning(f"{out_path} exists!")
        out_path.unlink()

    encoder = LaserEncoderPipeline(
        lang=None,
        model_dir=args.model_dir,
        laser="laser2"
    )

    # embed batches
    with EmbeddingConcatenator(out_path, fp16=True) as embed_fp:
        for batch_id in tqdm.tqdm(range(n_batches)):
            embeddings = encoder.encode_sentences(lines[batch_id * bsz:(batch_id + 1) * bsz])

            embed_fp.append_embedding_from_array(embeddings)

    logger.info(f"Finished!")


if __name__ == '__main__':
    _args = parse_args()
    main(_args)
