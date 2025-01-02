
from resverman.storage.handlers.storage_handler import StorageHandlerFactory


class ResourceDownloader:
    def __init__(self, storage_type: str, storage_config: dict):
        self.handler = StorageHandlerFactory.get_handler(storage_type, storage_config)

    def download(self, remote_relative_path: str) -> bytes:
        content = self.handler.download(remote_relative_path)
        return content
