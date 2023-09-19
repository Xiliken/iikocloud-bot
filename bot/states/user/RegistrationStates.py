from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    register_method = State()
    phone_number = State()  # Ввод номера телефона
    sms_code = State()  # Ввод СМС
    birthday = State()  # Дата рождения
