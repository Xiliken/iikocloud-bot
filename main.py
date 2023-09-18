import asyncio

from loguru import logger

from bot import start_bot
from api.iikocloud.iIkoCloud import BaseAPI

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')
