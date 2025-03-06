from pathlib import Path


RESOURCES_FOLDER_NAME = 'resources'
_RESOURCES_DIR = Path(__file__).parents[1] / RESOURCES_FOLDER_NAME


def get_resources_dir() -> Path:
    return _RESOURCES_DIR
