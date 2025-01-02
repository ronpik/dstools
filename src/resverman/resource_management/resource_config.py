
from dataclasses import dataclass
from pathlib import Path


from resverman.common.json_io import read_json


def get_src_root() -> Path:
    return Path(__file__).parent


_RVM_CONFIG_PATH = get_src_root() / 'rvs' / 'rvs.json'


@dataclass(frozen=True)
class ResourceConfig:
    resources_root: str
    remote_root: str
    remote_storage_type: str
    storage_config: dict

    @staticmethod
    def from_path(path: Path) -> 'ResourceConfig':
        config_data = read_json(path)
        storage = config_data.get("storage", {})
        resources_root_path = Path(config_data.get("resources_root")).expanduser()
        return ResourceConfig(
            resources_root=str(resources_root_path),
            remote_root=config_data.get("remote_root"),
            remote_storage_type=storage.get("remote_storage_type"),
            storage_config=storage.get("storage_config")
        )

    @staticmethod
    def default() -> 'ResourceConfig':
        return ResourceConfig.from_path(_RVM_CONFIG_PATH)

