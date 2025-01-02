import asyncio
from typing import Iterable, Sequence, Optional

from PIL.Image import Image

from resverman.common.image_utils.image_io import image_from_bytes, image_to_bytes_async
from resverman.data_manage.collections import AsyncDBCollectionWithContent, AsyncDBCollection, \
    GeneralAsyncFirestoreCollection
from resverman.data_manage.firestore import FirestoreCollectionClient
from resverman.data_manage.schema import RawPageMetadataRecord, RawPageRecord, LocationType
from resverman.storage.handlers.async_handler import AsyncStorageHandler


class RawPageCollectionWithContent(AsyncDBCollectionWithContent[RawPageMetadataRecord, RawPageRecord]):

    def __init__(
            self,
            name: str,
            firestore_client: FirestoreCollectionClient,
            async_storage: AsyncStorageHandler
    ):
        self._async_storage = async_storage
        self._metadata_collection = GeneralAsyncFirestoreCollection[RawPageMetadataRecord](
            name,
            RawPageMetadataRecord,
            firestore_client
        )

    @property
    def metadata_collection(self) -> AsyncDBCollection[RawPageMetadataRecord]:
        return self._metadata_collection

    @property
    def name(self) -> str:
        return self.metadata_collection.name


    async def _insert_items_content(self, input_items: Sequence[RawPageRecord]) -> Sequence[RawPageMetadataRecord]:
        async def insert_item_content(item: RawPageRecord) -> RawPageMetadataRecord:
            content = await self._get_content(item)
            content_path = f"{self.name}/{item.id}.{item.image.format}"
            await self._async_storage.upload(content, content_path)
            return RawPageMetadataRecord(item.id, item.page_id, item.page_hash, item.size, item.image.format, LocationType.GCS, content_path)

        tasks = list(map(insert_item_content, input_items))
        return await asyncio.gather(*tasks)


    async def _fetch_items_content(self, items_metadata: Iterable[RawPageMetadataRecord], content_fields: Optional[list[str]] = None) -> Iterable[RawPageRecord]:
        async def fetch_item_content(item: RawPageMetadataRecord) -> RawPageRecord:
            image: Optional[Image] = None
            if item.content_location:
                content = await self._async_storage.download(item.content_location)
                image = image_from_bytes(content)

            return RawPageRecord(item.id, item.page_id, item.page_hash, item.size, item.image_format, image)

        tasks = list(map(fetch_item_content, items_metadata))
        return await asyncio.gather(*tasks)

    @staticmethod
    async def _get_content(record: RawPageRecord) -> Optional[bytes]:
        if record.image is None:
            return b''

        return await image_to_bytes_async(record.image, record.image_format)
