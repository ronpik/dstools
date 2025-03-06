import time
from typing import Optional
from contextlib import ContextDecorator
from enum import Enum

from dstools.common.dummy_logger import PrintLogger, DummyLoggerLevel


try:
    from globalog import LOG, LoggerLeve
    _use_globalog = True
except ImportError:
    LOG = PrintLogger()
    LoggerLevel = DummyLoggerLevel
    _use_globalog = False

from dstools.common.ext.typing_ext import LoggerType


class TimeUnit(Enum):
    NANOSECONDS = 1e9
    MICROSECONDS = 1e6
    MILLISECONDS = 1e3
    SECONDS = 1


class DurationMeasure(ContextDecorator):
    """
    A context manager that measures the duration of code execution and logs the results.
    Automatically adjusts time units if the measured duration is too small for the specified unit.

    Args:
        action (str): Description of the action being measured
        log_start (bool, optional): Whether to log when the measurement starts. Defaults to False.
        log_end (bool, optional): Whether to log when the measurement ends. Defaults to True.
        log_level (int, optional): Logging level for messages. Defaults to LoggerLevel.INFO.
        unit (TimeUnit, optional): Desired time unit for measurements. Defaults to TimeUnit.MILLISECONDS.
        fallback (bool, optional): Whether to fallback to smaller units if duration is 0. Defaults to True.

    Example:
        >>> with DurationMeasure(action='processing data', unit=TimeUnit.MILLISECONDS):
        ...     # Your code here
        ...     pass
    """

    def __init__(
            self,
            action: str,
            logger: Optional[LoggerType] = None,
            log_start: bool = False,
            log_end: bool = True,
            log_level: int = LoggerLevel.INFO,
            unit: TimeUnit = TimeUnit.MILLISECONDS,
            fallback: bool = True
    ):
        self.action = action
        self.log_start = log_start
        self.log_end = log_end
        self.target_unit = unit
        self.fallback = fallback
        self.start_time = 0.0
        self.wall_start_time = 0.0
        self.duration = 0.0
        self.used_unit = unit
        # logging
        self._logger  = logger or LOG
        self.log_level = log_level


    def _format_duration(self, duration: float) -> tuple[float, TimeUnit]:
        """
        Formats the duration in the most appropriate unit.
        Returns the formatted value and the unit used.
        """
        if not self.fallback:
            return duration * self.target_unit.value, self.target_unit

        # Start with target unit
        current_unit = self.target_unit
        current_value = duration * current_unit.value

        # If duration is 0 in current unit, try smaller units
        while current_value == 0 and current_unit != TimeUnit.NANOSECONDS:
            if current_unit == TimeUnit.MILLISECONDS:
                current_unit = TimeUnit.MICROSECONDS
            elif current_unit == TimeUnit.MICROSECONDS:
                current_unit = TimeUnit.NANOSECONDS
            current_value = duration * current_unit.value

        return current_value, current_unit

    def _get_unit_suffix(self, unit: TimeUnit) -> str:
        """Returns the suffix for the time unit."""
        return {
            TimeUnit.NANOSECONDS: "ns",
            TimeUnit.MICROSECONDS: "µs",
            TimeUnit.MILLISECONDS: "ms",
            TimeUnit.SECONDS: "s"
        }[unit]

    def __enter__(self):
        self.start_time = time.perf_counter()
        self.wall_start_time = time.time()
        if self.log_start:
            LOG.log(self.log_level, f"Starting: {self.action}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        wall_elapsed = time.time() - self.wall_start_time

        formatted_duration, unit_used = self._format_duration(duration)
        unit_suffix = self._get_unit_suffix(unit_used)

        if self.log_end:
            if exc_type is not None:
                LOG.error(f"Failed: {self.action} "
                          f"(duration: {formatted_duration:.4f}{unit_suffix}, total: {wall_elapsed:.2f}s)",
                          exc_info=exc_val)
                raise exc_val

            LOG.log(
                self.log_level,
                f"Completed: {self.action} "
                f"(duration: {formatted_duration:.4f}{unit_suffix}, "
                f"total: {wall_elapsed:.2f}s)"
            )

        self.duration = formatted_duration
        self.used_unit = unit_used
        return False
