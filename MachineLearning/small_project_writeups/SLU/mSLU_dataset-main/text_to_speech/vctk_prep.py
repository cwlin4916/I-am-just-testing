# this script converts all VCTK audios into 16khz wav files.

import argparse
import glob
import logging
import os
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import tqdm

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger(Path(__file__).stem)


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
    parser.add_argument(
        "--ext",
        default="wav",
        type=str
    )
    return parser.parse_args()


def convert(
        in_aud: str,
        out_dir: Path,
        ext: str
):
    in_aud = Path(in_aud)
    out_path = out_dir / in_aud.parent.name / f"{in_aud.stem}.{ext}"
    out_path.parent.mkdir(exist_ok=True)
    success = os.system(
        f"ffmpeg -hide_banner -loglevel error -nostats -y -i {in_aud.as_posix()} -vn -ar 16000 -ac 1 {out_path.as_posix()}"
    )
    assert success == 0


def main(args):
    in_dir = Path(args.in_dir)
    ext = args.ext
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_inputs = glob.glob(
        (in_dir / "**" / "*.flac").as_posix(),
        recursive=True,
    )

    convert_ = partial(convert, out_dir=out_dir, ext=ext)
    with Pool(24) as p:
        _ = list(tqdm.tqdm(p.imap(convert_, all_inputs), total=len(all_inputs)))

    logger.info(f"Finished!")


if __name__ == "__main__":
    _args = parse_args()
    main(_args)
