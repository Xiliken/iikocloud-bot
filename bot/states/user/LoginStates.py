from aiogram.fsm.state import StatesGroup, State


class LoginStates(StatesGroup):
    phone_number = State()
    sms_code = State()
