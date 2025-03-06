import io

from PIL import Image


def is_valid_image(content: bytes) -> bool:
    dataBytesIO = io.BytesIO(content)
    try:
        Image.open(dataBytesIO)
    except (OSError, IOError):
        return False

    return True
