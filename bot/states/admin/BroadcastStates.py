from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    camp_text = State()
    add_button = State()
    button_text = State()
    button_url = State()
    confirmation = State()
