from typing import Literal, Optional
from pathlib import Path
import tarfile
import io

from research.compression.compressor import Compressor


_TarCompressionMode = Literal['gz', 'bz2', 'xz']


class FolderCompressor:

    def __init__(self, bytes_compressor: Compressor, mode: Optional[_TarCompressionMode] = None):
        """
        bytes_compressor: (Compressor) compressor implementation to use
        mode: (str) according to the described modes: https://docs.python.org/3.10/library/tarfile.html#tarfile.open
        """
        self._bytes_compressor = bytes_compressor
        self._mode = mode

    def compress_folder(self, folder_path: Path) -> bytes:
        """Compress the contents of a folder into bytes."""
        tar_buffer = io.BytesIO()
        mode = f'w:{self._mode}'
        with tarfile.open(fileobj=tar_buffer, mode=mode) as tar:
            tar.add(folder_path, arcname=folder_path.name)

        return self._bytes_compressor.compress(tar_buffer.getvalue())

    def decompress_to_folder(self, data: bytes, destination_folder: Path):
        """Decompress bytes and extract a folder to the destination."""
        decompressed_data = self._bytes_compressor.decompress(data)
        tar_buffer = io.BytesIO(decompressed_data)
        mode = f'r:{self._mode}'
        with tarfile.open(fileobj=tar_buffer, mode=mode) as tar:
            tar.extractall(path=destination_folder)
