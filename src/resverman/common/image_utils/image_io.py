from io import BytesIO
from pathlib import Path
from typing import Literal, Optional, cast

import PIL
from PIL.Image import Image
from globalog import LOG

from resverman.common.io_utils import write_bytes
from resverman.common.aio_utils import write_bytes as awrite_bytes

ImageFormat = {'png', 'tif', 'tiff', 'jpg', 'jpeg'}


def _resolve_format(path: Path, format: Optional[str] = None) -> str:
    if format is None:
        ext = path.suffix.lstrip('.').lower()
        assert_format(ext)
        return ext

    assert_format(format)
    return format


def assert_format(format: Optional[str]):
    if format is None:
        return

    if format.lower() not in ImageFormat:
        raise ValueError(f'Unsupported image format: {format}')


def image_to_bytes(image: Image, format: Optional[str] = None) -> bytes:
    format_ = format or image.format
    assert_format(format_)
    buffer = BytesIO()
    image.save(buffer, format_)
    return buffer.getvalue()


async def image_to_bytes_async(image: Image, format: Optional[str] = None) -> bytes:
    format_ = format or image.format
    assert_format(format_)
    buffer = BytesIO()
    try:
        image.save(buffer, format_)
    except OSError as e:
        LOG.error(f"An error (OSError) occurred during converting image to bytes: {image.size} : {image.format}", exc_info=True)
        return b''
    except AttributeError:
        LOG.error(f"An error occurred during converting image to bytes: {image} : {image.format}", exc_info=True)
        print('AttributeError', image, format)
        return b''

    return buffer.getvalue()


def image_from_bytes(content: bytes) -> Image:
    buffer = BytesIO(content)
    return PIL.Image.open(buffer)


def store_image(image: Image, path: Path, format: Optional[str] = None) -> Path:
    format_ = _resolve_format(path, format)
    if format_:
        path.with_suffix(format_)

    bytes_content = image_to_bytes(image, format_)
    write_bytes(path, bytes_content)
    return path


async def store_image_async(image: Image, path: Path, format: Optional[str] = None) -> Path:
    format_ = _resolve_format(path, format)
    if format_:
        path.with_suffix(format_)

    bytes_content = image_to_bytes(image, format_)
    await awrite_bytes(path, bytes_content)
    return path
