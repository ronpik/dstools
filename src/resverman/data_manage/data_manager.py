from typing import Sequence, Iterable, TypeVar, Any, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.async_stream_generator import AsyncStreamGenerator
from globalog import LOG

from resverman.common.async_iter_utils import async_chunked
from resverman.data_manage.collections import RawPageCollectionWithContent
from resverman.data_manage.firestore import FirestoreCollectionClient
from resverman.data_manage.collections.firestore_collection import GeneralAsyncFirestoreCollection
from resverman.data_manage.schema import RawPageRecord, RawPageMetadataRecord, EnrichedPageRecord, DataDBRecord
from resverman.storage.handlers.async_handler import AsyncStorageHandler


_T = TypeVar('_T', bound=DataDBRecord)


_RAW_PAGE_COLLECTION_NAME = 'raw_page'
_ENRICHED_PAGE_COLLECTION_NAME = 'enriched_page'

_DEFAULT_PAGINATE_SIZE = 10_000


class DataManager:
    def __init__(self, firestore_client: firestore.AsyncClient, async_handler: AsyncStorageHandler):
        """
        Initializes the DataManager with Firestore and storage clients and sets up collections.

        Args:
            firestore_client (FirestoreCollectionClient): The Firestore client for database interactions.
            async_handler (AsyncStorageHandler): The asynchronous handler for storage interactions.
        """
        self._firestore_client = firestore_client
        self._async_handler = async_handler

        self._raw_page_collection = RawPageCollectionWithContent(
            _RAW_PAGE_COLLECTION_NAME,
            FirestoreCollectionClient(_RAW_PAGE_COLLECTION_NAME, self._firestore_client),
            self._async_handler
        )

        self._enriched_page_collection = GeneralAsyncFirestoreCollection[EnrichedPageRecord](
            _ENRICHED_PAGE_COLLECTION_NAME,
            EnrichedPageRecord,
            FirestoreCollectionClient(_ENRICHED_PAGE_COLLECTION_NAME, self._firestore_client)
        )

    async def iterate_collection(self, collection: str, fields: Optional[Sequence[str]] = None) -> AsyncStreamGenerator[dict[str, Any]]:
        collection = self._firestore_client.collection(collection)
        if fields is not None and len(fields) > 0:
            iterator = collection.select(fields).stream()
        else:
            iterator = collection.stream()

        async for record in iterator:
            yield record.to_dict()

    async def iterate_record_ids(self, collection: str) -> AsyncStreamGenerator[str]:
        collection_ref = self._firestore_client.collection(collection)
        docs_iter = collection_ref.list_documents(_DEFAULT_PAGINATE_SIZE)
        chunks = async_chunked(docs_iter, _DEFAULT_PAGINATE_SIZE)
        async for doc_refs in chunks:
            for doc_ref in doc_refs:
                yield doc_ref.id

    async def iterate_collection_records(self, record_cls: DataDBRecord, collection: str, fields: Sequence[str]) -> AsyncStreamGenerator[dict[str, Any]]:
        dict_records = self.iterate_collection(collection, fields)
        async for record in dict_records:
            yield record_cls.from_json(record)

    async def insert_raw_pages(self, raw_pages: Sequence[RawPageRecord]) -> int:
        """
        Inserts raw page records with content into Firestore and storage.

        Args:
            raw_pages (Sequence[RawPageRecord]): A sequence of raw page records to insert.

        Returns:
            int: The number of raw page records successfully inserted.
        """
        result = await self._raw_page_collection.insert(raw_pages)
        return len(result)

    async def fetch_raw_pages(self, page_ids: Sequence[str]) -> Iterable[RawPageRecord]:
        """
        Fetches raw page records with content by their IDs.

        Args:
            page_ids (Sequence[str]): A sequence of page IDs to fetch.

        Returns:
            Sequence[RawPageRecord]: A sequence of fetched raw page records.
        """
        return await self._raw_page_collection.fetch(page_ids)

    async def fetch_raw_pages_metadata(self, page_ids: Sequence[str]) -> Iterable[RawPageMetadataRecord]:
        """
        Fetches metadata of raw pages by their IDs, without content.

        Args:
            page_ids (Sequence[str]): A sequence of page IDs to fetch metadata for.

        Returns:
            Sequence[RawPageMetadataRecord]: A sequence of raw page metadata records.
        """
        return await self._raw_page_collection.fetch_metadata(page_ids)

    async def insert_enriched_pages(self, enriched_pages: Sequence[EnrichedPageRecord]) -> int:
        """
        Inserts enriched page records into Firestore.

        Args:
            enriched_pages (Sequence[EnrichedPageRecord]): A sequence of enriched page records to insert.

        Returns:
            int: The number of enriched page records successfully inserted.
        """
        result = await self._enriched_page_collection.insert(enriched_pages)
        LOG.info(f'Inserted {len(result)} enriched page records.')
        return len(result)

    async def fetch_enriched_pages(self, page_ids: Sequence[str]) -> Iterable[EnrichedPageRecord]:
        """
        Fetches enriched page records by their IDs.

        Args:
            page_ids (Sequence[str]): A sequence of enriched page IDs to fetch.

        Returns:
            Sequence[EnrichedPageRecord]: A sequence of fetched enriched page records.
        """
        return await self._enriched_page_collection.fetch(page_ids)
