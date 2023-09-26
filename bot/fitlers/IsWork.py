from aiogram.filters import BaseFilter

from bot.mics import Config


class IsWork(BaseFilter):
    def __init__(self):
        pass

    def __call__(self):
        return Config.get("MAINTENANCE", "bool")
