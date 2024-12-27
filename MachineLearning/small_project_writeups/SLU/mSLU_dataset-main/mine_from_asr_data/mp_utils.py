import logging
import os
import sys
from multiprocessing import Process
from pathlib import Path

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    stream=sys.stdout,
)
logger = logging.getLogger(Path(__file__).stem)


def get_shard_range(tot: int, nshard: int, rank: int):
    assert rank < nshard and rank >= 0, f"invaid rank/nshard {rank}/{nshard}"
    start = round(tot / nshard * rank)
    end = round(tot / nshard * (rank + 1))
    assert start < end, f"start={start}, end={end}"
    logger.info(
        f"rank {rank} of {nshard}, process {end - start} "
        f"({start}-{end}) out of {tot}"
    )
    return start, end


def start_multi_processes(
        data: list,
        n_proc: int,
        func: callable,
        *args,
        **kwargs
):
    """
    It is required that the first argument of the function is process id,
        the second argument is the list of data.
    """
    assert n_proc > 0, f"{n_proc} should be larger than 0."

    if len(data) < n_proc:
        n_proc = len(data)

    if n_proc == 1:
        logger.info(f"Single process")
        func(0, data, *args, **kwargs)
    else:
        logger.info(f"Multi process")
        processes = []
        for pid in range(n_proc):
            start, end = get_shard_range(len(data), nshard=n_proc, rank=pid)
            processes.append(
                Process(
                    target=func,
                    args=(
                        pid,
                        data[start:end],
                        *args
                    ),
                    kwargs=kwargs
                )
            )
        for p in processes:
            p.start()
        for p in processes:
            p.join()
