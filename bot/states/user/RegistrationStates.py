from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    register_method = State()
    phone_number = State() # Ввод номера телефона
    sms_code = State() # Ввод СМС
    birthday = State() # Дата рождения
