from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    auth_method = State() # Выбор метода авторизации
    phone_number = State() # Ввод номера телефона
    sms_code = State() # Ввод СМС
