import os
from pathlib import Path

from globalog import LOG

RESOURCES_FOLDER_NAME = 'resources'
_RESOURCES_DIR = Path(__file__).parents[1] / RESOURCES_FOLDER_NAME


def get_resources_dir() -> Path:
    return _RESOURCES_DIR


def locate_rvs_config_file() -> Path:
    env_var = os.environ.get('RVS_CONFIG_FOLDER')

    if env_var:
        return Path(env_var) / 'rvs.json'

    cwd = Path.cwd()
    rvs_json_file = cwd / 'rvs.json'

    if rvs_json_file.exists():
        return rvs_json_file

    rvs_folder = cwd / 'rvs'
    rvs_json_file_in_folder = rvs_folder / 'rvs.json'

    if rvs_json_file_in_folder.exists():
        return rvs_json_file_in_folder

    LOG.warning('Could not locate rvs.json')
    return None

