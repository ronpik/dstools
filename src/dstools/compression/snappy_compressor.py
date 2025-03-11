import snappy

from research.compression.compressor import Compressor


class SnappyCompressor(Compressor):

    def compress(self, data: bytes) -> bytes:
        return snappy.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return snappy.uncompress(data)