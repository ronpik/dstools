from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Iterator, Sequence, List, Optional, Iterable, Callable

from resverman.common.iter_utils import take_first_iter
from resverman.data_manage.schema import DataDBRecord


_T = TypeVar('_T', bound=DataDBRecord)
_R = TypeVar('_R', bound=DataDBRecord)


class AsyncDBCollection(Generic[_T], ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[_T]:
        raise NotImplementedError

    async def insert_single(self, item: _T) -> Optional[str]:
        """
        insert item and return its id
        """
        ids = await self.insert([item])
        return ids[0][1]

    @abstractmethod
    async def insert(self, items: Sequence[_T]) -> List[tuple[int, str]]:
        """
        insert multiple items and return pairs of the item index as given with its id
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch(self, items_ids: Sequence[str]) -> Iterable[_T]:
        raise NotImplementedError

    async def fetch_single(self, items_id: str) -> Optional[_T]:
        item = take_first_iter(await self.fetch([items_id]))
        return item


class AsyncDBCollectionWithContent(Generic[_T, _R], ABC):

    @property
    @abstractmethod
    def metadata_collection(self) -> AsyncDBCollection[_T]:
        raise NotImplementedError

    @abstractmethod
    async def _insert_items_content(self, input_items: Sequence[_R]) -> Sequence[_T]:
        raise NotImplementedError

    @abstractmethod
    async def _fetch_items_content(self, items_metadata: Iterable[_T], content_fields: Optional[list[str]] = None) -> Iterable[_R]:
        raise NotImplementedError

    async def insert(self, items: Sequence[_R]) -> List[tuple[int, str]]:
        original_indices = {item.id: i for i, item in enumerate(items)}
        items_metadata = await self._insert_items_content(items)
        await self.metadata_collection.insert(items_metadata)
        return [(original_indices[item.id], item.id) for item in items_metadata]

    async def fetch_metadata(self, items_ids: Sequence[str]) -> Iterable[_T]:
        return await self.metadata_collection.fetch(items_ids)

    async def fetch(self, items_ids: Sequence[str], content_fields: Optional[list[str]] = None) -> Iterable[_R]:
        items_metadata = await self.fetch_metadata(items_ids)
        return await self._fetch_items_content(items_metadata, content_fields)
