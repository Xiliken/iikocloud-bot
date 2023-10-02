from aiogram.filters.state import State, StatesGroup


class ReviewStates(StatesGroup):
    food_rating = State()
    service_rating = State()
