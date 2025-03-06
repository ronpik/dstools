from __future__ import annotations
import abc
from typing import List, Dict, Protocol, TypeVar, overload, Iterator, Tuple, TYPE_CHECKING, ClassVar, Any, TypeAlias, \
    Mapping, Sequence, Any, Union

from typing_extensions import ParamSpec, Literal

from typing_extensions import reveal_type

_T_co = TypeVar("_T_co")


# https://github.com/python/typing/issues/182#issuecomment-1320974824
# All major type checkers now support recursive type aliases by default, so this should largely work:
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

# Note that because dict is invariant, you might run into some issues e.g. with dict[str, str].
# For such use cases you can use cast, and if you don't need mutability, something like the following might work:
JSON_ro: TypeAlias = Mapping[str, "JSON_ro"] | Sequence["JSON_ro"] | str | int | float | bool | None


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    @abc.abstractmethod
    def __lt__(self: _CT, other: _CT) -> bool:
        pass


_CT = TypeVar("_CT", bound=Comparable)


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]


P = ParamSpec('P')

# Common log levels
LogLevel = Union[int, Literal['TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']]


class LoggerType(Protocol):
    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a trace message (most detailed level)."""
        ...

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        ...

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        ...

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        ...

    def error(self, msg: str, *args: Any, exc_info: Any = None, **kwargs: Any) -> None:
        """Log an error message."""
        ...

    def critical(self, msg: str, *args: Any, exc_info: Any = None, **kwargs: Any) -> None:
        """Log a critical message (highest severity)."""
        ...

    def log(self, level: LogLevel, msg: str, *args: Any, **kwargs: Any) -> None:
        """Generic log method that accepts a level parameter."""
        ...

    def exception(self, msg: str, *args: Any, exc_info: bool = True, **kwargs: Any) -> None:
        """Log an exception (usually called from an except block)."""
        ...

    def setLevel(self, level: LogLevel) -> None:
        """Set the logging level."""
        ...

    def isEnabledFor(self, level: LogLevel) -> bool:
        """Check if this logger is enabled for the specified level."""
        ...
