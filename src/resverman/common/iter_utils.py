from __future__ import annotations

import heapq
from itertools import chain, islice
from operator import itemgetter
from typing import TypeVar, List, Iterable, Optional, Callable, Sequence, Generator, Container, Tuple

from resverman.common.ext.typing_ext import Comparable

_T = TypeVar('_T')
_R = TypeVar('_R')
_CT = TypeVar("_CT", bound=Comparable)


def iter_list(items: List[_T], start: int = 0, stop: int = -1) -> Iterable[_T]:
    if start < 0:
        raise ValueError("'start' must be non-negative integer")

    stop_ = len(items) if stop == -1 else stop
    if stop_ < 0:
        raise ValueError("'stop' must be non-negative integer, or -1 to reach until the end of the list.")

    yield from map(items.__getitem__, range(start, stop_))


def chunked(iterable: Iterable[_T], chunk_size: int) -> Generator[List[_T], None, None]:
    """Yield successive chunks from an iterable of type using islice."""
    it = iter(iterable)
    chunk = list(islice(it, chunk_size))
    while len(chunk) == chunk_size:
        yield chunk
        chunk = list(islice(it, chunk_size))

    if len(chunk) > 0:
        yield chunk


def iter_no_stop(iterable: Iterable[_T], default_value: _R = None) -> Generator[_T | _R]:
    yield from iterable
    while True:
        yield default_value


def merge_iters(*iterables: Iterable[_T], key: Callable[[_T], _CT]) -> Iterable[_T]:
    iterables = list(map(iter, iterables))
    items_q = []
    for i, it in enumerate(iterables):
        try:
            item = next(it)
            item_key = key(item)
            heapq.heappush(items_q, (item_key, i, item))
        except StopIteration:
            pass

    while len(items_q) > 0:
        _, iter_index, item = heapq.heappop(items_q)
        yield item

        try:
            item = next(iterables[iter_index])
            item_key = key(item)
            heapq.heappush(items_q, (item_key, iter_index, item))
        except StopIteration:
            pass


def take_first(seq: Sequence[_T], default_value: Optional[_T] = None) -> Optional[_T]:
    if len(seq) == 0:
        return default_value

    return seq[0]


def take_first_iter(iterable: Iterable[_T], default_value: Optional[_T] = None) -> Optional[_T]:
    try:
        return next(iter(iterable))
    except StopIteration:
        return default_value


def make_unique_seq(seq: Sequence[_T], keep_sorted: bool = True) -> Container[_T]:
    unique_seq = set(seq)
    if keep_sorted:
        return sorted(unique_seq)

    return unique_seq


def make_unique(iterable: Iterable[_T]) -> Iterable[_T]:
    seen_items = set()
    for item in iterable:
        if item not in seen_items:
            seen_items.add(item)
            yield item


def zip_map(func: Callable[[_T], _R], seq: Sequence[_T]) -> Iterable[Tuple[_T, _R]]:
    mapped = map(func, seq)
    return zip(seq, mapped)


def zip_map_r(func: Callable[[_T], _R], seq: Sequence[_T]) -> Iterable[Tuple[_R, _T]]:
    mapped = map(func, seq)
    return zip(mapped, seq)


def zip_map_iter(func: Callable[[_T], _R], iterable: Iterable[_T]) -> Iterable[Tuple[_T, _R]]:
    return ((item, func(item)) for item in iterable)


def zip_map_iter_r(func: Callable[[_T], _R], iterable: Iterable[_T]) -> Iterable[Tuple[_R, _T]]:
    return ((func(item), item) for item in iterable)


def partition(predicate: Callable[[_T], bool], iterable: Iterable[_T]) -> Tuple[List[_T], List[_T]]:
    partitioned = ([], [])

    def append(value: _T) -> int:
        index = int(bool(predicate(value)))
        partitioned[index].append(value)
        return index

    sum(map(append, iterable))
    return partitioned[1], partitioned[0]


def argmax(seq: Sequence[_T], key: Optional[Callable[[_T], _CT]] = None) -> int:
    if len(seq) == 0:
        raise ValueError('\'seq\' must not be empty')

    if key is None:
        key_ = itemgetter(1)
    else:
        key_ = lambda t: key(t[1])

    index, value = max(enumerate(seq), key=key_)
    return index


def chain_t(iterables: Iterable[Iterable[_T]]) -> Iterable[_T]:
    return chain.from_iterable(iterables)
