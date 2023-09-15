import random
from datetime import datetime

from aiogram import Router
from aiogram.enums import ContentType
from aiogram.filters import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram import F
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.iikocloud.enums import TypeRCI
from api.iikocloud.iIkoCloud import IikoCloudAPI
from api.sms_center import SMSC
from bot.database.models.User import User
from bot.fitlers import IsPhoneNumber
from bot.fitlers.CheckDateFilter import CheckDateFilter
from bot.fitlers.IsAuth import IsAuth
from bot.keyboards import register_kb, cabinet_main_kb, auth_kb
from bot.keyboards.reply import cancel_kb
from bot.mics import normalize_phone_number, check_telegram_account_exists
from bot.mics.helpers.Config import Config
from bot.mics.iikoapi import check_iiko_user_exists
from bot.states.user import RegistrationStates

router: Router = Router()
iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get('IIKOCLOUD_LOGIN'))

MAX_SMS_ATTEMPTS = 3
attempts = {}  # Количество попыток ввода кода
verification_code = random.randint(1000, 9999)


# Обработка регистрации
@router.message(Command(commands=['register', 'reg', 'registration']), StateFilter(default_state), ~IsAuth())
@router.message(F.text == '🔐 Регистрация', StateFilter(default_state), ~IsAuth())
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
    if await check_telegram_account_exists(msg):
        await msg.answer('❗Извините, но данный номер телефона зарегистрирован на другую учетную запись!')
        return

    iko_user = iiko.customer_info(
        organization_id=Config.get('IIKOCLOUD_ORGANIZATIONS_IDS', 'list')[0],
        type=TypeRCI.phone,
        identifier=msg.contact.phone_number
    )

    if check_iiko_user_exists(iko_user):
        await msg.answer(f'Извините, но пользователь, с номером +{msg.contact.phone_number} уже существует!\n\n'
                         f'Пожалуйста, повторите регистрацию с <b>другим номером</b>, или войдите с уже <u>существуещим номером</u>!')
        return



    # Устанавливаем состояния ожидания введения смс
    try:
        SMSC().send_sms(phones=f'{msg.contact.phone_number}',
                            message=f'Код: {str(verification_code)}\nВводя его вы даете согласие на обработку ПД.')
        await state.update_data(phone_number=msg.contact.phone_number)
        await state.set_state(RegistrationStates.sms_code)
        await msg.answer(f'Пожалуйста, введите проверочный код, отправленный на номер: {msg.contact.phone_number}',
                             reply_markup=cancel_kb())
    except Exception as ex:
        print(ex)


# region Регистрация с другого номера

# Обработка хендлера, если регистрация происходит с другого номера телефона
@router.message(StateFilter(RegistrationStates.register_method), F.text == 'Другой номер')
async def registration_step_other_phone(msg: Message, state: FSMContext):
    await msg.answer(text='Пожалуйста, введите номер телефона для регистрации', reply_markup=cancel_kb())


# Если пользователь выбрал способ регистрации с другим номером
# То проверяем данный номер и продолжаем регистрацию
@router.message(StateFilter(RegistrationStates.register_method), IsPhoneNumber())
async def check_phone_number_handler(msg: Message, state: FSMContext):
    await state.update_data(phone_number=normalize_phone_number(msg.text))

    state_data = await state.get_data()

    if await check_telegram_account_exists(msg):
        await msg.answer('❗Извините, но данный номер телефона зарегистрирован на другую учетную запись!')
        return

    iko_user = iiko.customer_info(
        organization_id=Config.get('IIKOCLOUD_ORGANIZATIONS_IDS', 'list')[0],
        type=TypeRCI.phone,
        identifier=state_data.get('phone_number')
    )

    if check_iiko_user_exists(iko_user):
        await msg.answer(f'Извините, но пользователь, с номером +{state_data.get("phone_number")} уже существует!\n\n'
                         f'Пожалуйста, повторите регистрацию с <b>другим номером</b>, или войдите с уже <u>существуещим номером</u>!')
        return
    else:
        # Устанавливаем состояния ожидания ввода смс
        try:
            # Вывод кода подтверждения в дебаге
            if Config.get('DEBUG', 'bool'):
                logger.debug(f'Код подтверждения: {verification_code}')

            SMSC().send_sms(phones=f'{state_data.get("phone_number")}',
                            message=f'Код: {str(verification_code)}\n'
                                    f'Вводя его вы даете согласие на обработку ПД')
            await state.set_state(RegistrationStates.sms_code)
            await msg.answer(
                f'Пожалуйста, введите проверочный код, отправленный на номер: +{normalize_phone_number(msg.text)}',
                reply_markup=cancel_kb())
        except Exception as ex:
            print(ex)


# region Обработка ввода СМС кода

@router.message(StateFilter(RegistrationStates.sms_code), F.text.isdigit())
async def registration_step_sms(msg: Message, state: FSMContext, session: AsyncSession):
    user_id = msg.from_user.id

    # Получаем текущее количество попыток из базы данных или переменной
    current_attempts = attempts.get(user_id, MAX_SMS_ATTEMPTS - 1)

    # Вывод кода подтверждения в дебаге
    if Config.get('DEBUG', 'bool'):
        logger.debug(f'Код подтверждения: {verification_code}')

    if msg.text == str(verification_code):
        # Код верен, выполните необходимые действия
        await msg.answer("🟢 Код успешно подтвержден!")
        attempts[user_id] = None  # Сброс количества попыток
        await state.set_state(RegistrationStates.birthday)  # Установка состояния - ввод даты рождения
        await msg.answer('Пожалуйста, укажите вашу дату рождения в формате: <b>дд.мм.гггг</b>')
    else:
        # Код неверен
        if current_attempts is not None and int(current_attempts) > 0:
            await msg.answer(f"🔴 Неверный код. Осталось попыток: {current_attempts}")
            attempts[user_id] = current_attempts - 1
        else:
            await msg.answer("🔴 Вы 3 раза ввели неверный код! Регистрация отменена!", reply_markup=auth_kb())
            # Сброс количества попыток
            attempts[user_id] = None
            await state.clear()


# Если введенно что-то некорректное
@router.message(StateFilter(RegistrationStates.sms_code))
async def warning_sms_handler(msg: Message):
    await msg.answer('Пожалуйста, введите 4х значный код, отправленный на ваш номер, указанный при регистрации!\n\n'
                     'Если Вы хотите прервать регистрацию - отправьте команду /cancel')


# Обработка ввода даты рождения пользователем
@router.message(StateFilter(RegistrationStates.birthday), CheckDateFilter())
async def registration_step_birthday_handler(msg: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    # Регистрация в IikoCloud и добавление в БД
    try:
        iiko.create_or_update_customer(
            organization_id=Config.get('IIKOCLOUD_ORGANIZATIONS_IDS', 'list')[0],
            phone=state_data.get('phone_number'),
            name=msg.from_user.first_name,
            sur_name=msg.from_user.last_name,
            birthday=datetime.strptime(msg.text, "%d.%m.%Y").strftime("%Y-%m-%d 00:00:00.000")
        )
        print('Добавлен в Iiko')
        try:
            await session.merge(
                User(user_id=msg.from_user.id, is_admin=False, phone_number=state_data['phone_number']))
            print('Добавлен в БД')
        except:
            print('Не удалось добавить пользователя в базу данных!')
    except Exception as ex:
        print('Ошибка регистрации нового пользователя!')
    await session.commit()
    await msg.answer('Регистрация успешно завершена!', reply_markup=cabinet_main_kb())

    # Сброс состояния
    await state.clear()


@router.message(StateFilter(RegistrationStates.birthday))
async def warning_birthday_handler(msg: Message):
    await msg.answer('Пожалуйста, введите дату рождения в формате: <b>дд.мм.гггг</b>\n\n'
                     'Если Вы хотите прервать регистрацию - отправьте команду /cancel')


# endregion


@router.message(Command(commands=['register', 'reg', 'registration']), StateFilter(default_state), IsAuth())
@router.message(F.text == '🔐 Регистрация', StateFilter(default_state), IsAuth())
async def auth_registration_step_regtype(msg: Message, state: FSMContext) -> None:
    await msg.answer(text='❗Вы уже авторизованы!', reply_markup=cabinet_main_kb())