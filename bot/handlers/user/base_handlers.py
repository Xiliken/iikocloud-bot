from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.User import User
from bot.keyboards import auth_kb
from bot.keyboards.cabinet import cabinet_main_kb
from bot.keyboards.inline import (
    chat_inline_kb,
    contacts_ikb,
    hr_ikb,
    promotions_ikb,
    website_ikb,
)
from bot.mics.const_functions import clear_text

router: Router = Router()


# Обработчик команды "/start"
@router.message(CommandStart(), StateFilter(default_state))
async def __start(msg: Message, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
    bot: Bot = msg.bot
    user_id = msg.from_user.id
    user = msg.from_user

    sql = await session.execute(select(User).where(User.user_id == user_id))
    # Если такой пользователь уже существует
    if sql.scalar():
        await msg.answer(
            _("Привет, <b>{first_name}</b> 🤗\n" "Выбери в меню интересующую функцию ⬇️\n").format(
                first_name=user.first_name
            ),
            reply_markup=cabinet_main_kb(),
            parse_mode="HTML",
        )
    else:
        await msg.answer(
            _(
                "Привет! Я чат-бот стрит-фуд ресторана <b><a href='https://doners-club.ru'>Донерс</a></b>.\n"
                "Со мной тебя ждут скидки и специальные цены на продукцию, кэшбэк с каждой покупки, "
                "бонусы за отзывы и оценку заказов.\n\n"
                'Авторизуйся 1 раз и получай все преимущества "Doners-club" 😎'
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=auth_kb(),
        )

    await session.commit()


# Обработчик кнопки и команды "Меню"
@router.message(F.text == __("Меню"))
async def menu_handler(msg: Message):
    await msg.answer(_("Нажмите ниже, чтобы открыть меню"), reply_markup=website_ikb())


# Обработчик кнопки "Акции"
@router.message(F.text == __("Акции"))
async def promotions_handler(msg: Message):
    await msg.answer(
        _("Нажмите на кнопку, чтобы просмотреть доступные акции"),
        reply_markup=promotions_ikb(),
    )


# Обработчик кнопки и команды "Чат"
@router.message(F.text == __("Чат"))
@router.message(Command(commands=["chat"]))
async def chat_handler(msg: Message) -> None:
    await msg.answer(_("Нажми на кнопку и напиши свой вопрос"), reply_markup=chat_inline_kb())


# Обработчик кнопки и команды "Контакты"
@router.message(F.text == __("Контакты"))
@router.message(Command(commands=["contacts", "contact"]))
async def chat_handler(msg: Message) -> None:
    await msg.answer(_("Выбери ресторан:"), reply_markup=contacts_ikb())


@router.message(F.text == __("Работа"))
@router.message(Command(commands=["work", "job"]))
async def work_handler(msg: Message) -> None:
    await msg.answer(
        clear_text(
            _(
                """
        Донерс - это не только ресторан и доставка! Мы большая команда 😎
        Мы ищем как сотрудников в общепит, так и офисных работников.
        Также у нас много друзей, которым нужны классные ребята с опытом работы и без 😉
        Напиши нам и мы предложим тебе вакансии на выбор!
        """
            )
        ),
        reply_markup=hr_ikb(),
    )
