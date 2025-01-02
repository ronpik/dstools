from typing import List, Iterable, Sequence, Iterator, Callable, Optional, Type, TypeVar
import asyncio

from research.data_manage.collections import AsyncDBCollection
from research.data_manage.firestore import FirestoreCollectionClient
from research.data_manage.schema import DataDBRecord


_T = TypeVar('_T', bound=DataDBRecord)

_MAX_BATCH_SIZE = 500


class GeneralAsyncFirestoreCollection(AsyncDBCollection[_T]):
    def __init__(self, name: str, item_cls: Type[_T], firestore_client: FirestoreCollectionClient):
        self._name = name
        self._item_cls = item_cls
        self._firestore_client = firestore_client

    @property
    def name(self) -> str:
        return self._name

    def __iter__(self) -> Iterator[_T]:
        # Placeholder for iteration logic if needed in the future
        raise NotImplementedError("Iteration is not implemented for this collection")

    async def insert(self, items: Sequence[_T]) -> list[tuple[int, str]]:
        """
        Inserts multiple items into Firestore using batch operations.

        Args:
            items (Sequence[_T]): The items to insert.

        Returns:
            List[tuple[int, str]]: A list of tuples containing the index and ID of each inserted item.
        """
        results = await self._firestore_client.add_many([item.to_json() for item in items])
        return results

    async def fetch(self, items_ids: Sequence[str]) -> Iterable[_T]:
        items_data = await self._firestore_client.get_many(items_ids)
        results = [self._item_cls.from_json(item_data) for item_data in items_data]
        # async def fetch_item(item_id: str) -> Optional[_T]:
        #     item_data = await self._firestore_client.get_document(item_id)
        #     if item_data is not None:
        #         return self._item_cls.from_json(item_data)  # Assume _T can be constructed from dict
        #
        #     return None
        #
        # tasks = [fetch_item(item_id) for item_id in items_ids]
        # results = await asyncio.gather(*tasks)
        return results
