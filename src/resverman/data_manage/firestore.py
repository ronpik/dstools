from google.api_core import retry
from google.api_core.exceptions import DeadlineExceeded
from google.cloud import firestore
from typing import Optional, Any, Sequence, TypedDict, Iterable

from research.common.iter_utils import chunked
from research.logs.logger import LOG

MAX_BATCH_SIZE = 500    # Firestore batch can handle up to 500 writes

Item = TypedDict('Item', {'id': str})



class FirestoreCollectionClient:
    def __init__(self, collection_name: str, firestore_client: firestore.AsyncClient):
        self.firestore_client = firestore_client
        self.collection_name = collection_name
        self._collection_ref = firestore_client.collection(self.collection_name)

    async def add_document(self, doc_id: str, data: dict[str, Any]):
        doc_ref = self._collection_ref.document(doc_id)
        await doc_ref.set(data)

    async def get_document(self, doc_id: str) -> Optional[dict[str, Any]]:
        doc_ref = self._collection_ref.document(doc_id)
        doc_snapshot = await doc_ref.get()
        if doc_snapshot.exists:
            return doc_snapshot.to_dict()

        return None

    async def add_many(self, items: Sequence[Item]) -> list[tuple[int, str]]:
        """
        Inserts multiple items into Firestore using batch operations.

        Args:
            items (Sequence[_T]): The items to insert.

        Returns:
            List[tuple[int, str]]: A list of tuples containing the index and ID of each inserted item.
        """
        retry_policy = retry.AsyncRetry(predicate=retry.if_exception_type(DeadlineExceeded), timeout=3600)

        results = []
        batch_offset = 0
        for batch_items in chunked(items, MAX_BATCH_SIZE):
            batch = self.firestore_client.batch()
            for index, item in enumerate(batch_items):
                doc_ref = self._collection_ref.document(item['id'])
                batch.set(doc_ref, item)

            try:
                changes = await batch.commit(retry_policy)
                LOG.info(f"Batch commited with {len(changes)} changes")
                LOG.debug(f"Batch commited with {len(batch_items)} items to insert: {changes}")
            except Exception as e:
                LOG.error(f"Batch commit failed: {e}", exc_info=True)
                continue

            results.extend([(batch_offset + index, item['id']) for index, item in enumerate(batch_items)])
            batch_offset += len(batch_items)

        return results

    async def get_many(self, items_ids: Sequence[str]) -> Iterable[Item]:
        """
        Fetches multiple items from Firestore using bulk reads.

        Args:
            items_ids (Sequence[str]): The IDs of the items to fetch.

        Returns:
            Iterable[_T]: An iterable of the fetched items.
        """
        # Firestore allows fetching multiple documents using get_all
        doc_refs = [self._collection_ref.document(item_id) for item_id in items_ids]
        documents = self.firestore_client.get_all(doc_refs)
        results = []
        async for doc in documents:
            if doc.exists:
                item = doc.to_dict()
                results.append(item)
        return results