from typing import AsyncIterable, List, AsyncGenerator, TypeVar

_T = TypeVar('_T')


async def async_chunked(iterable: AsyncIterable[_T], chunk_size: int) -> AsyncGenerator[List[_T], None]:
    """Yield successive chunks from an async iterable."""
    chunk = []
    async for item in iterable:
        chunk.append(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []

    # Yield any remaining items if they don't make a full chunk
    if chunk:
        yield chunk
