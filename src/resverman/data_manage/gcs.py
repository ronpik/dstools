from PIL import Image
import io

from research.storage.handlers.async_handler import AsyncStorageHandler


class AsyncGCSClient:
    def __init__(self, async_handler: AsyncStorageHandler):
        self.async_handler = async_handler

    async def download_image(self, remote_relative_path: str) -> Image.Image:
        """Download an image asynchronously and convert it from bytes."""
        compressed_data = await self.async_handler.download(remote_relative_path)
        image = Image.open(io.BytesIO(compressed_data))
        return image

    async def upload_image(self, image: Image.Image, remote_relative_path: str) -> bool:
        """Upload an image asynchronously after converting it to bytes."""
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr = img_byte_arr.getvalue()

        return await self.async_handler.upload(img_byte_arr, remote_relative_path)