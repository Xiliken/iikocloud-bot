from aiogram.fsm.state import State, StatesGroup


class FeedbackSates(StatesGroup):
    food_rating = State()
    service_rating = State()
