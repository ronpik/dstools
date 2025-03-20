import inspect
from abc import ABCMeta, ABC
from pathlib import Path
from typing import Optional

from globalog import LOG

from dstools.compression.folder_compress import FolderCompressor
from dstools.compression.snappy_compressor import SnappyCompressor
from dstools.resource_management.resource_storage.resource_downloader import ResourceDownloader
from dstools.resource_management.resource_storage.resource_uploader import ResourceUploader
from dstools.resource_management.resource_config import ResourceConfig
from dstools.resource_management.resource_utils import locate_rvs_config_file


CONFIG_PATH = locate_rvs_config_file()
if CONFIG_PATH is None:
    _CONFIG = ResourceConfig.default()
else:
    _CONFIG = ResourceConfig.from_path(CONFIG_PATH)


def is_abstract(cls: type, bases: tuple[type, ...]) -> bool:
    if inspect.isabstract(cls):
        return True

    return ABC in bases


class ResourceMeta(ABCMeta):
    _instances = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        resource_name: Optional[str] = kwargs.pop('resource_name', None)
        version: Optional[str] = kwargs.pop('version', None)

        cls = super().__new__(mcs, name, bases, namespace)

        if not is_abstract(cls, bases):
            if not (resource_name and version):
                raise ValueError(f"Couldn't construct a resource class with class args: {resource_name=} ; {version=}")

            cls._resource_name = resource_name
            cls._version = version
            cls._local_path = Path(_CONFIG.resources_root).expanduser() / resource_name / f'V{version}'
            cls._remote_relative_path = f"{_CONFIG.remote_root}/{resource_name}/V{version}"

        return cls

    def __call__(cls, *args, **kwargs):
        # Singleton logic based on resource name and version
        key = (cls._resource_name, cls._version)
        if key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[key] = instance
        return cls._instances[key]


class Resource(ABC, metaclass=ResourceMeta):
    """
    Abstract base class for resources.
    This class should be inherited by all resource classes.

    Example Usage:

    ..  code-block:: python
    class ExampleResource(Resource, resource_name='example', version='1.0'):
    def __init__(self):
        super().__init__()
        self.example_file_path = self.local_path / 'example.txt'

    def get_example_data(self) -> list[str]:
        with open(self.stopwords_path, 'r') as f:
            return f.read()

    """

    def __init__(self):
        self.name = self._resource_name
        self.version = self._version
        self.local_path = self._local_path
        self.remote_relative_path = self._remote_relative_path
        self._loaded = False
        self.load()

    def load(self) -> 'Resource':
        if self._loaded:
            LOG.debug(f"Resource already loaded: {self.name}:{self.version} ")
            return self

        self._loaded = True
        if self.local_path.exists():
            LOG.info(f"Resource {self.name} v{self.version} exists")
            return self

        LOG.info(f"Resource {self.name} v{self.version} not found locally, fetching from remote")
        downloader = ResourceDownloader(_CONFIG.remote_storage_type, _CONFIG.storage_config)
        compressed_bytes = downloader.download(self.remote_relative_path)

        # Decompress into a folder
        LOG.info(f"Decompressed content to {self.local_path.parent}")
        compressor = self._get_folder_compressor()
        compressor.decompress_to_folder(compressed_bytes, self.local_path.parent)
        return self

    def upload(self):
        compressed_bytes = self._get_folder_compressor().compress_folder(self.local_path)
        ResourceUploader(_CONFIG.remote_storage_type, _CONFIG.storage_config)\
            .upload(compressed_bytes, self.remote_relative_path)

    @staticmethod
    def _get_folder_compressor() -> FolderCompressor:
        bytes_compressor = SnappyCompressor()
        compressor = FolderCompressor(bytes_compressor, mode='gz')
        return compressor
