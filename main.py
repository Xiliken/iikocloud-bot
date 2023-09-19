import asyncio

from loguru import logger

from api.iikocloud.iIkoCloud import BaseAPI
from bot import start_bot

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
