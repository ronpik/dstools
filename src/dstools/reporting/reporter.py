from pathlib import Path
from datetime import datetime
import json
import csv
from typing import Optional, Union, TextIO, Dict, Any, Callable
import inspect
from functools import wraps


class Reporter:
    _instance = None

    def __init__(self):
        self._enabled = False
        self._base_path: Optional[Path] = None

    @classmethod
    def get_instance(cls) -> 'Reporter':
        if cls._instance is None:
            cls._instance = Reporter()
        return cls._instance

    def _get_script_name(self) -> str:
        """Get the name of the script that initialized the reporter."""
        frame = inspect.stack()[-1]
        script_path = Path(frame.filename)
        return script_path.stem

    def initialize(self, folder: Optional[Path] = None) -> None:
        """Initialize the reporter with an optional custom folder."""
        self._enabled = True

        if folder is not None:
            self._base_path = Path(folder)
        else:
            # Create default path: ~/.dono/reports/<script_name>/<timestamp>
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_name = self._get_script_name()
            self._base_path = Path.home() / '.dono' / 'reports' / script_name / timestamp

        # Create the directory if it doesn't exist
        self._base_path.mkdir(parents=True, exist_ok=True)

    @property
    def base_path(self) -> Optional[Path]:
        return self._base_path

    @property
    def is_enabled(self) -> bool:
        return self._enabled


class ReportWriter:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self._file: Optional[TextIO] = None
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def write_json(self, data: Dict[str, Any]) -> None:
        """Write data as JSON."""
        with open(self.filepath.with_suffix('.json'), 'w') as f:
            json.dump(data, f, indent=2)

    def write_csv(self, data: list, headers: Optional[list] = None) -> None:
        """Write data as CSV."""
        with open(self.filepath.with_suffix('.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(headers)
            writer.writerows(data)

    def write_plain_text(self, text: str) -> None:
        with open(self.filepath, 'w') as f:
            f.write(text)

    def write_bytes(self, data: bytes) -> None:
        with open(self.filepath, 'wb') as f:
            f.write(data)


def init_report(folder: Optional[Path] = None) -> None:
    """Initialize the global reporter."""
    Reporter.get_instance().initialize(folder)


def report(filename: Union[str, Path]) -> Callable:
    """
    Decorator that handles report generation.
    The decorated function should accept a ReportWriter instance as its only parameter.
    """

    def decorator(func: Callable[[ReportWriter, ...], None]) -> Callable[[...], None]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            reporter = Reporter.get_instance()
            if reporter.is_enabled and reporter.base_path:
                filepath = reporter.base_path / filename
                writer = ReportWriter(filepath)
                return func(writer, *args, **kwargs)
            return None

        return wrapper

    return decorator