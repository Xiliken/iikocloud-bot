import random
from enum import Enum

import aiogram_i18n.types
from aiogram import Router
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

MAX_SMS_ATTEMPTS = 3
verification_code = random.randint(1000, 9999)

res = iiko.customer_info(
    organization_id='09b5076e-4a9a-46f7-8857-bc02e21c07ad',
    type=TypeRCI.phone,
    identifier='79130478769'
)


# Обработка регистрации
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


@router.message(F.content_type == ContentType.CONTACT, StateFilter(RegistrationStates.register_method))
async def registration_step_telegram(msg: Message, state: FSMContext):
    # TODO: Проверить, что такого пользователя нет в IikoCloud
    is_iko_user = iiko.customer_info(
        organization_id=Config.get('IIKOCLOUD_ORGANIZATIONS_IDS', 'list')[0],
        type=TypeRCI.phone,
        identifier=msg.contact.phone_number
    )

    # Устанавливаем состояния ожидания введения смс
    try:
        await state.set_state(RegistrationStates.sms_code)
        await msg.answer(f'Пожалуйста, введите проверочный код, отправленный на номер: +{msg.contact.phone_number}',
                         reply_markup=aiogram_i18n.types.ReplyKeyboardRemove())
    except Exception as ex:
        log(ex)


# Обработка ввода СМС кода
@router.message(StateFilter(RegistrationStates.sms_code))
async def registration_step_sms(msg: Message, state: FSMContext):
    # Получаем текущее количество попыток из состояния
    current_attempts = await state.get_data()
    current_attempts = current_attempts.get('attempts', MAX_SMS_ATTEMPTS - 1)

    print(verification_code)

    if msg.text == str(verification_code):
        # Код верен, выполните необходимые действия, например, переведите пользователя в следующее состояние
        await state.update_data(attempts=MAX_SMS_ATTEMPTS)  # Сброс количества попыток
        await state.clear()
        await msg.answer("🟢 Код успешно подтвержден!")
    else:
        # Код неверен
        if current_attempts > 0:
            await msg.answer(f"🔴 Неверный код. Осталось попыток: {current_attempts}")
            await state.update_data(attempts=current_attempts - 1)
        else:
            await msg.answer("🔴 Вы 3 раза ввели неверный код! Регистрация отменена!")
            await state.clear()


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
