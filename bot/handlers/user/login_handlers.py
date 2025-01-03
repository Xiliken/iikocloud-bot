import datetime
import random

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import bot.mics.iikocloudapi
from bot.database.models.User import User
from bot.fitlers import IsPhoneNumber
from bot.fitlers.IsAuth import IsAuth
from bot.keyboards import cabinet_main_kb
from bot.keyboards.reply import auth_kb, cancel_kb
from bot.mics import check_telegram_account_exists, normalize_phone_number
from bot.mics.helpers.Config import Config
from bot.states.user.LoginStates import LoginStates
from services.iikocloud.enums import TypeRCI
from services.iikocloud.iIkoCloud import IikoCloudAPI
from services.sms_center import SMSC

router: Router = Router()
iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get("IIKOCLOUD_LOGIN"))

MAX_SMS_ATTEMPTS = 3
attempts = {}  # Количество попыток ввода кода
# verification_code = random.randint(1000, 9999)


@router.message(Command(commands=["login"]), StateFilter(default_state), ~IsAuth())
@router.message(F.text == __("🔑 Авторизация"), StateFilter(default_state), ~IsAuth())
async def login_step_one(msg: Message, state: FSMContext) -> None:
    await msg.answer(text=_("Пожалуйста, введите номер телефона"), reply_markup=cancel_kb())
    await state.set_state(LoginStates.phone_number)


@router.message(StateFilter(LoginStates.phone_number), IsPhoneNumber())
async def login_step_phone_number(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    # Проверка номера в Telegram
    if await check_telegram_account_exists(msg):
        await msg.answer(_("❗Извините, но данный номер телефона зарегистрирован на другую учетную запись!"))
        return

    # Проверить, есть ли такой номер в iko
    iiko_user = iiko.customer_info(
        organization_id=Config.get("IIKOCLOUD_ORGANIZATIONS_IDS", "list")[0],
        type=TypeRCI.phone,
        identifier=normalize_phone_number(msg.text),
    )

    if bot.mics.iikocloudapi.check_iiko_user_exists(iiko_user):
        try:
            verification_code = random.randint(1000, 9999)

            (
                SMSC().send_sms(
                    phones=f"{normalize_phone_number(msg.text)}",
                    message=_("Код: {verification_code}\nВводя его вы даете согласие на обработку ПД").format(
                        verification_code=str(verification_code)
                    ),
                )
            )
            await state.update_data(verification_code=verification_code)
            await state.update_data(phone_number=normalize_phone_number(msg.text))

            await state.set_state(LoginStates.sms_code)
            await msg.answer(
                _("Пожалуйста, введите проверочный код, отправленный по СМС на номер: +{phone}").format(
                    phone=normalize_phone_number(msg.text)
                ),
                reply_markup=cancel_kb(),
            )
        except Exception as ex:
            logger.error(ex)
        await session.commit()
    else:
        # Пользователя не существует
        await state.clear()
        await msg.answer(
            _(
                "Извините, не удалось найти пользователя с номером +{phone}\n\n"
                "Пожалуйста, проверьте корректность введенного номера, или зарегистрируйте новый аккаунт!"
            ).format(phone=normalize_phone_number(msg.text)),
            reply_markup=auth_kb(),
        )
        return


@router.message(StateFilter(LoginStates.sms_code), F.text.isdigit())
async def login_step_sms(msg: Message, state: FSMContext, session: AsyncSession):
    user_id = msg.from_user.id
    data = await state.get_data()
    verification_code = data.get("verification_code")

    # Получаем текущее количество попыток из базы данных или переменной
    current_attempts = attempts.get(user_id, MAX_SMS_ATTEMPTS - 1)

    # Вывод кода подтверждения в дебаге
    if Config.get("DEBUG", "bool"):
        logger.debug(f"Код подтверждения: {verification_code}")

    if msg.text == str(verification_code):
        # Код верен, выполните необходимые действия
        await msg.answer(_("🟢 Код успешно подтвержден!"))
        attempts[user_id] = None  # Сброс количества попыток
        await session.merge(
            User(
                user_id=msg.from_user.id,
                phone_number=normalize_phone_number(data.get("phone_number")),
                is_admin=False,
                registration_date=datetime.datetime.now(),
            )
        )
        await session.commit()
        await msg.answer(_("✔️Авторизация успешно завершена!"), reply_markup=cabinet_main_kb())

        data.clear()  # Очищаем хранилище

        # Сброс состояния
        await state.clear()
    else:
        # Код неверен
        if current_attempts is not None and int(current_attempts) > 0:
            await msg.answer(
                _("🔴 Неверный код. Осталось попыток: {current_attempts}").format(current_attempts=current_attempts)
            )
            attempts[user_id] = current_attempts - 1
        else:
            await msg.answer(
                _("🔴 Вы {max_sms_attempts} раза ввели неверный код! Авторизация отменена!").format(
                    max_sms_attempts=MAX_SMS_ATTEMPTS
                ),
                reply_markup=auth_kb(),
            )
            # Сброс количества попыток
            attempts[user_id] = None
            await state.clear()


# Если введенно что-то некорректное
@router.message(StateFilter(LoginStates.sms_code))
async def warning_sms_handler(msg: Message):
    await msg.answer(
        _(
            "Пожалуйста, введите 4х значный код, отправленный на ваш номер, указанный при регистрации!\n\n"
            "Если Вы хотите прервать авторизацию - отправьте команду /cancel"
        )
    )


@router.message(Command(commands=["login"]), StateFilter(default_state), IsAuth())
@router.message(F.text == __("🔑 Авторизация"), StateFilter(default_state), IsAuth())
async def auth_registration_step_regtype(msg: Message, state: FSMContext) -> None:
    await msg.answer(text=_("❗Вы уже авторизованы!"), reply_markup=cabinet_main_kb())
