import json
from pathlib import Path
from typing import Iterable, Iterator

from resverman.common.ext.typing_ext import JSON
from resverman.common.io_utils import write_lines, read_lines


def write_json(data:JSON, path: str):
    with open(path, 'w') as f:
        json.dump(data, f)


def read_json(path: str | Path) -> JSON:
    with open(path) as f:
        return json.load(f)


def write_json_lines(path: str | Path, data: Iterable[JSON]):
    lines = map(json.dumps, data)
    write_lines(path, lines)


def read_json_lines(path: str | Path) -> Iterator[JSON]:
    lines = read_lines(path)
    yield from map(json.loads, lines)
