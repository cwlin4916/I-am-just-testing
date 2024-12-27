import csv
import json
from typing import List


def read_vox_tsv(path) -> List[str]:
    res = []
    with open(path) as fp:
        fp.readline()
        for line in fp:
            _, raw_text, norm_text, _, _ = line.strip().split("\t")
            assert raw_text or norm_text
            text: str = norm_text if norm_text else raw_text
            text = text.lower()
            res.append(text)
    return res


def read_commonvoice_tsv(path) -> List[str]:
    res = []
    with open(path) as fp:
        for item in csv.DictReader(fp, delimiter="\t"):
            res.append(item["sentence"])
    return res


def read_massive_jsonl(path) -> List[str]:
    res = []
    with open(path) as fp:
        for line in fp:
            utt = json.loads(line.strip())["utt"]
            res.append(utt)
    return res


def read_router(path, data_type: str) -> List[str]:
    if data_type == "massive":
        return read_massive_jsonl(path)
    elif data_type == "voxpopuli":
        return read_vox_tsv(path)
    elif data_type == "commonvoice":
        return read_commonvoice_tsv(path)
    else:
        raise NotImplementedError(f"{data_type} not supported!")


def read_lines(path) -> List[str]:
    with open(path) as fp:
        res = []
        for line in fp:
            res.append(line.strip())
    return res
