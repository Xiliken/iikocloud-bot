import random

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import bot.mics.iikoapi
from api.iIkoCloud.enums import TypeRCI
from api.iIkoCloud.iIkoCloud import IikoCloudAPI
from api.sms_center import SMSC
from bot.database.models.User import User
from bot.fitlers import IsPhoneNumber
from bot.keyboards import cabinet_main_kb
from bot.keyboards.reply import cancel_kb, auth_kb
from bot.mics import normalize_phone_number
from bot.mics.helpers.Config import Config
from bot.states.user.LoginStates import LoginStates

router: Router = Router()
iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get('IIKOCLOUD_LOGIN'))

MAX_SMS_ATTEMPTS = 3
attempts = {}  # Количество попыток ввода кода
verification_code = random.randint(1000, 9999)


@router.message(Command(commands=['login']), StateFilter(default_state))
@router.message(F.text == '🔑 Авторизация', StateFilter(default_state))
async def login_step_one(msg: Message, state: FSMContext) -> None:
    await msg.answer(text='Пожалуйста, введите номер телефона', reply_markup=cancel_kb())
    await state.set_state(LoginStates.phone_number)


@router.message(StateFilter(LoginStates.phone_number), IsPhoneNumber())
async def login_step_phone_number(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    # Проверить, есть ли такой номер в iko
    iiko_user = iiko.customer_info(organization_id=Config.get('IIKOCLOUD_ORGANIZATIONS_IDS', 'list')[0],
                                   type=TypeRCI.phone,
                                   identifier=normalize_phone_number(msg.text),
                                   )

    if bot.mics.iikoapi.check_user_exists(iiko_user):
        # Пользователь существует в iko, но проверяем на то, что пользователь с таким ID в Telegram не зарегистрирован на другой номер
        sql = await session.execute(select(User).where(User.user_id == msg.from_user.id and normalize_phone_number(User.phone_number) != normalize_phone_number(msg.text)))

        if sql.scalar():
            await msg.answer('Извините, но данный аккаунт Telegram привязан к другому номеру телефона!', reply_markup=auth_kb())
            await state.clear()
            return
        else:
            # Добавляем пользователя в бд
            try:
                await session.merge(User(user_id=msg.from_user.id, phone_number=normalize_phone_number(msg.text), is_admin=False))
                SMSC().send_sms(phones=f'{normalize_phone_number(msg.text)}',
                                message=f'Код для подтверждения авторизации: {str(verification_code)}')
                await state.set_state(LoginStates.sms_code)
                await msg.answer(f'Пожалуйста, введите проверочный код, отправленный на номер: +{normalize_phone_number(msg.text)}',
                                 reply_markup=cancel_kb())
            except Exception as ex:
                print(ex)
        await session.commit()
    else:
        # Пользователя не существует
        await state.clear()
        await msg.answer(f'Извините, не удалось найти пользователя с номером +{normalize_phone_number(msg.text)}\n\n'
                         f'Пожалуйста, проверьте корректность введенного номера, или зарегистрируйте новый аккаунт!',
                         reply_markup=auth_kb())
        return


@router.message(StateFilter(LoginStates.sms_code), F.text.isdigit())
async def login_step_sms(msg: Message, state: FSMContext, session: AsyncSession):
    user_id = msg.from_user.id

    # Получаем текущее количество попыток из базы данных или переменной
    current_attempts = attempts.get(user_id, MAX_SMS_ATTEMPTS - 1)
    print(verification_code)

    if msg.text == str(verification_code):
        # Код верен, выполните необходимые действия
        state_data = await state.get_data()

        await msg.answer("🟢 Код успешно подтвержден!")
        attempts[user_id] = None # Сброс количества попыток
        await session.commit()
        await msg.answer('Авторизация успешно завершена!', reply_markup=cabinet_main_kb())

        # Сброс состояния
        await state.clear()
    else:
        # Код неверен
        if current_attempts is not None and int(current_attempts) > 0:
            await msg.answer(f"🔴 Неверный код. Осталось попыток: {current_attempts}")
            attempts[user_id] = current_attempts - 1
        else:
            await msg.answer("🔴 Вы 3 раза ввели неверный код! Авторизация отменена!", reply_markup=auth_kb())
            # Сброс количества попыток
            attempts[user_id] = None
            await state.clear()


# Если введенно что-то некорректное
@router.message(StateFilter(LoginStates.sms_code))
async def warning_sms_handler(msg: Message):
    await msg.answer('Пожалуйста, введите 4х значный код, отправленный на ваш номер, указанный при регистрации!\n\n'
                     'Если Вы хотите прервать авторизацию - отправьте команду /cancel')