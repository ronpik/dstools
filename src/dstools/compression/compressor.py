

from abc import ABC, abstractmethod


class Compressor(ABC):
    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        raise NotImplementedError()
