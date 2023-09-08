from enum import Enum

from aiogram import Dispatcher, Router, Bot
from aiogram.enums import ContentType, content_type
from aiogram.filters import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ChatMemberUpdated
from aiogram import F

from api.iIkoCloud.enums import TypeRCI
from api.iIkoCloud.iIkoCloud import IikoCloudAPI
from api.sms_center import SMSC
from bot.fitlers import IsPhoneNumber
from bot.keyboards import register_kb, cabinet_main_kb
from bot.mics import check_phone_number, log
from bot.mics.helpers.Config import Config
from bot.states.user import RegistrationStates

router: Router = Router()
iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get('IIKOCLOUD_LOGIN'))

res = iiko.customer_info(
    organization_id='09b5076e-4a9a-46f7-8857-bc02e21c07ad',
    type=TypeRCI.phone,
    identifier='79130478769'
)



# Обработка выбора ввода номера телефона от пользователя
@router.message(Command(commands=['register', 'reg', 'registration']), StateFilter(default_state))
@router.message(F.text == '🔐 Регистрация', StateFilter(default_state))
async def registration_step_regtype(msg: Message, state: FSMContext) -> None:
    await msg.answer(text=
                     'Пожалуйста, выберите способ регистрации в системе.',
                     parse_mode='HTML',
                     reply_markup=register_kb(),
                     )
    # Устанавливаем состояния ожидания выбора регистрации в системе
    await state.set_state(RegistrationStates.register_method)


# Обработка хендлера, если регистрация происходит с номера Telegram
#
#   Примерный план:
#   1. Сохраняем следующие данные о пользователе в Redis:
#       - id (Которое с телеги)
#       - name (Имя пользователя)
#       - phone (Номер телефона с телеграмма)
#       - registration_date (Дата регистрации)
#   2. Отправляем СМС с кодом подтверждения (узнать откуда)
#   3. Ожидаем ввода от пользователя
#   4. В будущем можно предложить дозаполнить анкету
#   5. Регистрируем пользователя в системе
@router.message(F.content_type == ContentType.CONTACT, StateFilter(RegistrationStates.register_method))
async def registration_step_telegram(msg: Message, state: FSMContext):
    # Устанавливаем состояния ожидания введения смс
    try:
        await state.clear()
        await msg.answer('Регистрация прошла успешно! Добро пожаловать в личный кабинет.',
                         reply_markup=cabinet_main_kb())
    except Exception as ex:
        log(ex)


# Обработка хендлера, если регистрация происходит с другого номера телефона
@router.message(StateFilter(RegistrationStates.register_method), F.text == 'Другой номер')
async def registration_step_other_phone(msg: Message):
    await msg.answer(text='Пожалуйста, введите номер телефона для регистрации')
    # Устанавливаем состояния ожидания введения смс


# Если пользователь выбрал способ регистрации с другим номером
# То проверяем данный номер и продолжаем регистрацию
@router.message(StateFilter(RegistrationStates.register_method), IsPhoneNumber())
async def check_phone_number_handler(msg: Message, state: FSMContext):
    await state.set_state(RegistrationStates.sms_code)
    await msg.answer(f"Вы ввели номер телефона {msg.text}")
    pass

# @router.message(StateFilter(RegistrationStates.phone_number))
# async def registration_step_phone_number(msg: Message, state: FSMContext) -> None:
#     await msg.answer('Ты прошел')
