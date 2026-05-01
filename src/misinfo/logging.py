from __future__ import annotations

import sys

from loguru import logger

from misinfo.config import get_settings


def configure_logging() -> None:
    logger.remove()
    logger.add(sys.stderr, level=get_settings().log_level)


__all__ = ["logger", "configure_logging"]
