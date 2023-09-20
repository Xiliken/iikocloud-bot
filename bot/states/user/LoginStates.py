from aiogram.fsm.state import State, StatesGroup


class LoginStates(StatesGroup):
    phone_number = State()
    sms_code = State()
