import logging
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


def setup_loger(level: Union[str, int] = "DEBUG", ignored: List[str] = ""):
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.getLevelName(level))
    for ignore in ignored:
        logger.disable(ignore)


def setup_logger_file(log_file: str, level: Union[str, int] = "DEBUG", ignored: List[str] = ""):
    logger.remove()  # Удалить стандартные обработчики вывода
    logger.add(log_file, rotation="500 MB", level=level, )  # Установить файловый обработчик логов

    for ignore in ignored:
        logger.disable(ignore)
