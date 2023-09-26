from loguru import logger

from .admin import router
from .user import __start, router

logger.info("All handlers are successfully configured")
