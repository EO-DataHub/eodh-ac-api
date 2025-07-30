from __future__ import annotations

import contextlib
import logging
import time
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from src import consts

if TYPE_CHECKING:
    from collections.abc import Generator

T = TypeVar("T")
P = ParamSpec("P")


def get_logger(name: str, log_level: int | str = logging.INFO) -> logging.Logger:
    """Builds a `Logger` instance with provided name and log level.

    Args:
        name: The name for the logger.
        log_level: The default log level.

    Returns:
        The logger.

    """
    logger = logging.getLogger(name=name)
    logger.setLevel(log_level)

    # Prevent log messages from propagating to the parent logger
    logger.propagate = False

    # Check if handlers are already set to avoid duplication
    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt=consts.logging.FORMAT)
        stream_handler.setFormatter(fmt=formatter)
        logger.addHandler(stream_handler)

    return logger


_timed_logger = get_logger("timed", log_level=logging.INFO)


@contextlib.contextmanager
def timing_context(name: str) -> Generator[None]:
    """Prints the execution time for the decorated function.

    Notes:
        Can also act as a context manager.

    Args:
        name: The name of the wrapped execution block.

    Returns:
        A context manager that prints the execution time.

    """
    _timed_logger.info("%(func_name)s is running...", {"func_name": name})
    t0 = time.monotonic()
    try:
        yield
    finally:
        t1 = time.monotonic()
        _timed_logger.info(
            "%(func_name)s ran in %(execution_time)s",
            {
                "func_name": name,
                "execution_time": f"{(t1 - t0):.4f}",
            },
        )
