from globalog import LOG

from resverman.storage.handlers.storage_handler import StorageHandlerFactory

class ResourceUploader:
    def __init__(self, storage_type: str, storage_config: dict):
        self._storage_type = storage_type
        self.handler = StorageHandlerFactory.get_handler(storage_type, storage_config)

    def upload(self, content: bytes, remote_relative_path: str):
        LOG.debug(f"Upload {len(content)} bytes to {self._storage_type} at {remote_relative_path}")
        self.handler.upload(content, remote_relative_path)
        LOG.debug(f"Uploaded {remote_relative_path} to {self._storage_type}.")
