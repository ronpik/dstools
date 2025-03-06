from pathlib import Path
from typing import Iterable, Iterator


def write_text(path: str | Path, content: str):
    with open(path, 'w') as f:
        f.write(content)


def read_text(path: str | Path) -> str:
    with open(path) as f:
        return f.read()


def write_bytes(path: str | Path, content: bytes):
    with open(path, 'wb') as f:
        f.write(content)


def read_bytes(path: str | Path) -> bytes:
    with open(path, 'rb') as f:
        return f.read()


def write_lines(path: str | Path, lines: Iterable[str]):
    with open(path, 'w') as f:
        for line in lines:
            f.write(line)
            f.write('\n')


def read_lines(path: str | Path) -> Iterator[str]:
    with open(path) as f:
        yield from f
