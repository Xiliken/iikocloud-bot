import random
from datetime import datetime

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.User import User
from bot.fitlers import IsPhoneNumber
from bot.fitlers.CheckDateFilter import CheckDateFilter
from bot.fitlers.IsAuth import IsAuth
from bot.keyboards import auth_kb, cabinet_main_kb, register_kb
from bot.keyboards.reply import cancel_kb
from bot.mics import check_telegram_account_exists, normalize_phone_number
from bot.mics.helpers.Config import Config
from bot.mics.iikocloudapi import check_iiko_user_exists
from bot.states.user import RegistrationStates
from services.iikocloud.enums import TypeRCI
from services.iikocloud.iIkoCloud import IikoCloudAPI
from services.sms_center import SMSC

router: Router = Router()
iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get("IIKOCLOUD_LOGIN"))

MAX_SMS_ATTEMPTS = 3
attempts = {}  # Количество попыток ввода кода


# Обработка регистрации
@router.message(
    Command(commands=["register", "reg", "registration"]),
    StateFilter(default_state),
    ~IsAuth(),
)
@router.message(F.text == __("🔐 Регистрация"), StateFilter(default_state), ~IsAuth())
async def registration_step_regtype(msg: Message, state: FSMContext) -> None:
    await msg.answer(
        text=_("Пожалуйста, выберите способ регистрации в системе."),
        parse_mode="HTML",
        reply_markup=register_kb(),
    )
    # Устанавливаем состояния ожидания выбора регистрации в системе
    await state.set_state(RegistrationStates.register_method)


@router.message(
    F.content_type == ContentType.CONTACT,
    StateFilter(RegistrationStates.register_method),
)
async def registration_step_telegram(msg: Message, state: FSMContext):
    if await check_telegram_account_exists(msg):
        await msg.answer(_("❗Извините, но данный номер телефона зарегистрирован на другую учетную запись!"))
        return

    iko_user = iiko.customer_info(
        organization_id=Config.get("IIKOCLOUD_ORGANIZATIONS_IDS", "list")[0],
        type=TypeRCI.phone,
        identifier=msg.contact.phone_number,
    )

    if check_iiko_user_exists(iko_user):
        await msg.answer(
            _(
                "Извините, но пользователь, с номером +{phone} уже существует!\n\n"
                "Пожалуйста, повторите регистрацию с <b>другим номером</b>, или войдите с уже "
                "<u>существующим номером</u>!"
            ).format(phone=msg.contact.phone_number)
        )
        return

    # Устанавливаем состояния ожидания введения смс
    try:
        verification_code = random.randint(1000, 9999)

        SMSC().send_sms(
            phones=f"{msg.contact.phone_number}",
            message=_("Код: {verification_code}\nВводя его вы даете согласие на обработку ПД.").format(
                verification_code=str(verification_code)
            ),
        )
        await state.update_data()
        await state.update_data(phone_number=msg.contact.phone_number)
        await state.update_data(verification_code=verification_code)
        await state.set_state(RegistrationStates.sms_code)
        await msg.answer(
            f"Пожалуйста, введите проверочный код, отправленный по СМС на номер: {msg.contact.phone_number}",
            reply_markup=cancel_kb(),
        )
    except Exception as ex:
        print(ex)


# region Регистрация с другого номера


# Обработка хендлера, если регистрация происходит с другого номера телефона
@router.message(StateFilter(RegistrationStates.register_method), F.text == __("Другой номер"))
async def registration_step_other_phone(msg: Message, state: FSMContext):
    await msg.answer(
        text=_("Пожалуйста, введите номер телефона для регистрации"),
        reply_markup=cancel_kb(),
    )


# Если пользователь выбрал способ регистрации с другим номером
# То проверяем данный номер и продолжаем регистрацию
@router.message(StateFilter(RegistrationStates.register_method), IsPhoneNumber())
async def check_phone_number_handler(msg: Message, state: FSMContext):
    await state.update_data(phone_number=normalize_phone_number(msg.text))

    state_data = await state.get_data()

    if await check_telegram_account_exists(msg):
        await msg.answer(_("❗Извините, но данный номер телефона зарегистрирован на другую учетную запись!"))
        return

    iko_user = iiko.customer_info(
        organization_id=Config.get("IIKOCLOUD_ORGANIZATIONS_IDS", "list")[0],
        type=TypeRCI.phone,
        identifier=state_data.get("phone_number"),
    )

    if check_iiko_user_exists(iko_user):
        await msg.answer(
            _(
                "Извините, но пользователь, с номером +{phone} уже существует!\n\n"
                "Пожалуйста, повторите регистрацию с <b>другим номером</b>, или войдите с уже "
                "<u>существующим номером</u>!"
            ).format(phone=state_data.get("phone_number"))
        )
        return
    else:
        # Устанавливаем состояния ожидания ввода смс
        try:
            verification_code = random.randint(1000, 9999)
            # Вывод кода подтверждения в дебаге
            if Config.get("DEBUG", "bool"):
                logger.debug(f"Код подтверждения: {verification_code}")

            SMSC().send_sms(
                phones=f'{state_data.get("phone_number")}',
                message=_("Код: {verification_code}\n" "Вводя его вы даете согласие на обработку ПД").format(
                    verification_code=str(verification_code)
                ),
            )
            await state.update_data(verification_code=verification_code)
            await state.set_state(RegistrationStates.sms_code)
            await msg.answer(
                _("Пожалуйста, введите проверочный код, отправленный по СМС на номер: +{phone}").format(
                    phone=normalize_phone_number(msg.text)
                ),
                reply_markup=cancel_kb(),
            )
        except Exception as ex:
            print(ex)


# region Обработка ввода СМС кода


@router.message(StateFilter(RegistrationStates.sms_code), F.text.isdigit())
async def registration_step_sms(msg: Message, state: FSMContext, session: AsyncSession):
    user_id = msg.from_user.id
    data = await state.get_data()

    # Получаем текущее количество попыток из базы данных или переменной
    current_attempts = attempts.get(user_id, MAX_SMS_ATTEMPTS - 1)

    # Вывод кода подтверждения в дебаге
    if Config.get("DEBUG", "bool"):
        logger.debug(f"Код подтверждения: {data.get('verification_code')}")

    if msg.text == str(data.get("verification_code")):
        # Код верен, выполните необходимые действия
        await msg.answer(_("🟢 Код успешно подтвержден!"))
        attempts[user_id] = None  # Сброс количества попыток
        await state.set_state(RegistrationStates.birthday)  # Установка состояния - ввод даты рождения
        await msg.answer(_("Пожалуйста, укажите вашу дату рождения в формате: <b>дд.мм.гггг</b>"))
    else:
        # Код неверен
        if current_attempts is not None and int(current_attempts) > 0:
            await msg.answer(
                _("🔴 Неверный код. Осталось попыток: {current_attempts}").format(current_attempts=current_attempts)
            )
            attempts[user_id] = current_attempts - 1
        else:
            await msg.answer(
                _("🔴 Вы {max_sms_attempts} раза ввели неверный код! Регистрация отменена!").format(
                    max_sms_attempts=MAX_SMS_ATTEMPTS
                ),
                reply_markup=auth_kb(),
            )
            # Сброс количества попыток
            attempts[user_id] = None
            await state.clear()


# Если введенно что-то некорректное
@router.message(StateFilter(RegistrationStates.sms_code))
async def warning_sms_handler(msg: Message):
    await msg.answer(
        _(
            "Пожалуйста, введите 4х значный код, отправленный на ваш номер, указанный при регистрации!\n\n"
            "Если Вы хотите прервать регистрацию - отправьте команду /cancel"
        )
    )


# Обработка ввода даты рождения пользователем
@router.message(StateFilter(RegistrationStates.birthday), CheckDateFilter())
async def registration_step_birthday_handler(msg: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    # Регистрация в IikoCloud и добавление в БД
    try:
        iiko.create_or_update_customer(
            organization_id=Config.get("IIKOCLOUD_ORGANIZATIONS_IDS", "list")[0],
            phone=state_data.get("phone_number"),
            name=msg.from_user.first_name,
            sur_name=msg.from_user.last_name,
            birthday=datetime.strptime(msg.text, "%d.%m.%Y").strftime("%Y-%m-%d 00:00:00.000"),
        )
        print("Добавлен в Iiko")
        try:
            await session.merge(
                User(
                    user_id=msg.from_user.id,
                    is_admin=False,
                    phone_number=state_data["phone_number"],
                    registration_date=datetime.now(),
                    last_order_date=None,
                    is_blocked=0,
                )
            )
            print("Добавлен в БД")
        except:
            print("Не удалось добавить пользователя в базу данных!")
    except Exception as ex:
        print("Ошибка регистрации нового пользователя!")
    await session.commit()
    await msg.answer(_("✔️Регистрация успешно завершена!"), reply_markup=cabinet_main_kb())

    # Сброс состояния
    await state.clear()


@router.message(StateFilter(RegistrationStates.birthday))
async def warning_birthday_handler(msg: Message):
    await msg.answer(
        _(
            "Пожалуйста, введите дату рождения в формате: <b>дд.мм.гггг</b>\n\n"
            "Если Вы хотите прервать регистрацию - отправьте команду /cancel"
        )
    )


# endregion


@router.message(
    Command(commands=["register", "reg", "registration"]),
    StateFilter(default_state),
    IsAuth(),
)
@router.message(F.text == __("🔐 Регистрация"), StateFilter(default_state), IsAuth())
async def auth_registration_step_regtype(msg: Message, state: FSMContext) -> None:
    await msg.answer(text=_("❗Вы уже авторизованы!"), reply_markup=cabinet_main_kb())
