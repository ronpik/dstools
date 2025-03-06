import aiofiles
from typing import Union, Iterable, AsyncIterator
from pathlib import Path


async def write_text(path: Union[str, Path], content: str):
    async with aiofiles.open(path, 'w') as f:
        await f.write(content)


async def read_text(path: Union[str, Path]) -> str:
    async with aiofiles.open(path, 'r') as f:
        return await f.read()


async def write_bytes(path: Union[str, Path], content: bytes) -> int:
    async with aiofiles.open(path, 'wb') as f:
        length = await f.write(content)
        return length


async def read_bytes(path: Union[str, Path]) -> bytes:
    async with aiofiles.open(path, 'rb') as f:
        return await f.read()


async def write_lines(path: Union[str, Path], lines: Iterable[str]):
    async with aiofiles.open(path, 'w') as f:
        for line in lines:
            await f.write(f"{line}\n")


async def read_lines(path: Union[str, Path]) -> AsyncIterator[str]:
    async with aiofiles.open(path, 'r') as f:
        async for line in f:
            yield line.rstrip('\n')
