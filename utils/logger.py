import logging
import pathlib
import sys
from typing import List, Union

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger(level: Union[str, int] = "DEBUG", ignored: List[str] = ""):
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:DD.MM.YYYY HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    for ignore in ignored:
        logger.disable(ignore)


def setup_logger_file(log_file: Union[pathlib.Path, str], level: Union[str, int] = "DEBUG", ignored: List[str] = ""):
    logger.remove()

    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.add(log_file, rotation="500 MB", enqueue=True, compression="tar.gz")

    for ignore in ignored:
        logger.disable(ignore)
