import glob
import logging
import os
from pathlib import Path
from typing import List

import soundfile
import tqdm

from mine_from_asr_data.mp_utils import start_multi_processes

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logger = logging.getLogger(Path(__file__).stem)


def convert(
        pid: int,
        file_names: List[str],
        output_dir: Path,
        ext: str
):
    for f_path in tqdm.tqdm(file_names, desc=f"[Proc {pid}]"):
        f_path = Path(f_path)
        if not f_path.exists():
            continue

        out_path = (output_dir / f"{f_path.name}").with_suffix(ext)
        if out_path.exists():
            continue

        tmp_out_path = output_dir / f"{f_path.stem}.tmp{ext}"
        success = os.system(
            f"ffmpeg -hide_banner -loglevel error -nostats -y -i {f_path.as_posix()} -vn -ar 16000 -ac 1 {tmp_out_path.as_posix()}"
        )

        if success == 0:
            tmp_out_path.replace(out_path)
            # make sure the audio can be read
            soundfile.info(out_path.as_posix())
        else:
            logger.error(f"Something wrong with {f_path}")
            if tmp_out_path.exists():
                tmp_out_path.unlink()


def main():
    in_dir = Path("/export/corpora5/CommonVoice/en_1488h_2019-12-10/clips/")
    out_dir = Path("/export/b12/cmeng9/CommonVoice/en_1488h_2019-12-10/clips")

    all_inputs = glob.glob(
        (in_dir / "*.mp3").as_posix()
    )

    start_multi_processes(
        data=all_inputs,
        n_proc=16,
        func=convert,
        output_dir=out_dir,
        ext=".flac"
    )
    logger.info(f"Finished!")


if __name__ == '__main__':
    main()
