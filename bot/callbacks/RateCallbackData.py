from aiogram.filters.callback_data import CallbackData


class RateCallbackData(CallbackData, prefix="rate"):
    food_rating: int


class RateServiceCallbackData(CallbackData, prefix="rate_service"):
    rating: int
