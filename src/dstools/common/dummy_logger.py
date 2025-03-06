import logging
from typing import Any, Union
import datetime


_levelToName = {
    logging.CRITICAL: 'CRITICAL',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'NOTSET',
}


class DummyLoggerLevel:
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class PrintLogger:
    def __init__(self, name: str = "PrintLogger") -> None:
        self.name = name
        self._enabled_level = "TRACE"  # Always enabled for all levels

    def _log(self, level: str, msg: str, *args: Any, exc_info: Any = None, **kwargs: Any) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

        # Format the message with args if provided
        if args:
            try:
                msg = msg % args
            except TypeError:
                msg = f"{msg} {' '.join(str(arg) for arg in args)}"

        # Print the formatted log message
        print(f"{timestamp} | {level:8} | {self.name} | {msg}")

        # Handle exception info if provided
        if exc_info:
            if isinstance(exc_info, bool) and exc_info:
                import sys
                exc_info = sys.exc_info()
            if isinstance(exc_info, tuple):
                import traceback
                print(''.join(traceback.format_exception(*exc_info)))
            elif isinstance(exc_info, BaseException):
                import traceback
                print(''.join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__)))

    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("TRACE", msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("DEBUG", msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("INFO", msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log("WARNING", msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, exc_info: Any = None, **kwargs: Any) -> None:
        self._log("ERROR", msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, *args: Any, exc_info: Any = None, **kwargs: Any) -> None:
        self._log("CRITICAL", msg, *args, exc_info=exc_info, **kwargs)

    def log(self, level: Union[str, int], msg: str, *args: Any, **kwargs: Any) -> None:
        if isinstance(level, int):
            level_str = _levelToName[level]
        else:
            level_str = level

        self._log(str(level_str).upper(), msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, exc_info: bool = True, **kwargs: Any) -> None:
        self._log("ERROR", msg, *args, exc_info=exc_info or True, **kwargs)

    def setLevel(self, level: str) -> None:
        self._enabled_level = str(level).upper()

    def isEnabledFor(self, level: str) -> bool:
        return True  # Always enabled for simplicity


# Example usage:
if __name__ == "__main__":
    logger = PrintLogger("MyApp")

    # Basic logging
    logger.info("Application starting...")
    logger.debug("Debug message with args: %s, %d", "test", 42)
    logger.warning("Warning message")

    # Logging with exception
    try:
        raise ValueError("Something went wrong")
    except Exception as e:
        logger.error("An error occurred", exc_info=e)
        logger.exception("Same error using exception method")

    # Using log method
    logger.log("INFO", "Custom log level message")

    # Critical error
    logger.critical("Critical system error", exc_info=False)