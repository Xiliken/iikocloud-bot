import asyncio
import datetime
import os
import zipfile

import loguru
from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.methods.user import get_admins
from bot.fitlers import IsAdmin
from bot.keyboards.admin.inline_admin import admin_users_ikb, get_confirm_button_ikb
from bot.keyboards.admin.reply_admin import admin_main_kb
from bot.mics.const_functions import clear_text, get_stats
from bot.states.admin.BroadcastStates import BroadcastStates

router: Router = Router()
router.message.filter(IsAdmin())


@router.message(Command(commands=["stats"]))
@router.message(F.text == __("📊 Статистика"))
async def admin_stats_handler(msg: Message, bot: Bot):
    # Нужно для того, чтобы пользователь видел, что бот что-то печатает, а не просто висит
    await bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)

    stats = await get_stats()

    department_incomes = stats.get("department_incomes")
    department_incomes_text = ""
    for department in department_incomes:
        department_name = department.get("department_name")
        income_today = department.get("income_today")
        income_yesterday = department.get("income_yesterday")
        income_per_week = department.get("income_per_week")

        department_incomes_text += f"""
        <b>💸 {department_name}</b>
        ┣ Доход за вчера: <code>{income_yesterday:,}</code>
        ┣ Доход за сегодня: <code>{income_today:,}</code>
        ┗ Доход за неделю: <code>{income_per_week:,}</code>
        """

    message = clear_text(
        _(
            """
            <b>📊 СТАТИСТИКА БОТА</b>
            ➖➖➖➖➖➖➖➖➖➖

            <b>👤 ПОЛЬЗОВАТЕЛИ</b>
            ┣ Регистраций за <b>сегодня</b>: <code>{reg_day_count}</code>
            ┣ Регистраций за <b>неделю</b>: <code>{reg_week_count}</code>
            ┣ Регистраций за <b>месяц</b>: <code>{reg_month_count}</code>
            ┣ Регистраций за <b>все время</b>: <code>{reg_all_time_count}</code>
            ┗ Пользователей, <b>заблокировавшие бота</b>: <code>{bot_blocked_count}</code>

            <b> ⭐️ ОТЗЫВЫ</b>
            ┣ Общее количество отзывов: <code>{reviews_total}</code>
            ┣ Положительных отзывов: <code>{reviews_positive}</code>
            ┗ Отрицательных отзывов: <code>{reviews_negative}</code>

            <b> 💰 ДОХОД</b>
            {department_incomes_text}
        """
        ).format(
            reg_day_count=stats.get("reg_users_today"),
            reg_week_count=stats.get("reg_users_week"),
            reg_month_count=stats.get("reg_users_month"),
            reg_all_time_count=stats.get("reg_users_all"),
            reviews_total=stats.get("total_reviews"),
            reviews_order_positive=stats.get("reviews_order_positive"),
            reviews_order_negative=stats.get("reviews_order_negative"),
            reviews_service_negative=stats.get("reviews_service_negative"),
            reviews_positive=stats.get("total_positive_reviews"),
            reviews_negative=stats.get("total_negative_reviews"),
            reviews_avg_order_rating=stats.get("reviews_avg_order_rating"),
            reviews_avg_service_rating=stats.get("reviews_avg_service_rating"),
            bot_blocked_count=stats.get("bot_blocked"),
            department_incomes_text=department_incomes_text,
        )
    )

    await msg.answer(message, parse_mode="HTML")


@router.message(Command(commands=["admin", "ap", "admin_panel"]))
async def admin_panel_handler(msg: Message):
    await msg.answer(
        _(
            "✅ Добро пожаловать в панель управления, <b>{user}</b>! Выберите нужный раздел для дальнейшей работы!"
        ).format(user=msg.from_user.full_name),
        reply_markup=admin_main_kb(),
    )


@router.message(F.text == __("🙍 Пользователи"))
async def admin_list_handler(msg: Message):
    await get_admins()

    await msg.answer(_("Пожалуйста, выберите пункт меню"), reply_markup=admin_users_ikb())


@router.message(Command(commands=["broadcast", "sender"]), F.text)
@router.message(F.text == __("📣 Рассылка"))
async def broadcast_admin_handler(msg: Message, state: FSMContext, command: CommandObject = CommandObject):
    if command is None:
        return

    if command.args is None:
        await msg.answer(
            clear_text(
                _(
                    """
                    Для создания новой рассылки пожалуйста введите название рассылки!
                    Для этого используйте: /sender [название рассылки]
                    """
                )
            )
        )
        return

    camp_name = command.args

    await msg.answer(
        clear_text(
            _(
                """
    Начинаю создание рассылки: <b>"{camp_name}"</b>
    Пожалуйста, введите <b><u>сообщение</u></b>, которое хотите отправить!
    """
            ).format(camp_name=camp_name)
        )
    )

    await state.update_data(camp_name=camp_name)
    await state.set_state(BroadcastStates.camp_text)


@router.message(BroadcastStates.camp_text, F.text)
async def camp_text_handler(msg: Message, state: FSMContext):
    await state.update_data(camp_message=msg.text)
    await msg.answer(
        clear_text(
            _(
                """
    Отлично! Я запомнил текст, который ты хочешь отправить!
    <u>Будем добавлять кнопку?</u>
    """
            )
        ),
        reply_markup=get_confirm_button_ikb(),
    )

    await state.update_data(message_id=msg.message_id, chat_id=msg.from_user.id)
    await state.set_state(BroadcastStates.add_button)


@router.callback_query(BroadcastStates.add_button)
async def add_button_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    if call.data == "add_button":
        await state.set_state(BroadcastStates.button_text)
        await call.message.answer(text=_("Отправьте текст для кнопки!"), reply_markup=None)
    elif call.data == "no_button":
        await call.message.edit_reply_markup(reply_markup=None)
        data = await state.get_data()
        message_id = int(data.get("message_id"))
        chat_id = int(data.get("chat_id"))
        await confirm_broadcast(message=call.message, bot=bot, chat_id=chat_id, message_id=message_id)

    await call.answer()


@router.message(BroadcastStates.button_text)
async def button_text_handler(msg: Message, state: FSMContext):
    await state.update_data(button_text=msg.text)
    await msg.answer(_("Введите ссылку для кнопки"))
    await state.set_state(BroadcastStates.button_url)


@router.message(BroadcastStates.button_url)
async def button_url_handler(msg: Message, state: FSMContext, bot: Bot):
    await state.update_data(button_url=msg.text)
    added_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=(await state.get_data()).get("button_text"), url=msg.text)]]
    )
    data = await state.get_data()
    message_id = int(data.get("message_id"))
    chat_id = int(data.get("chat_id"))
    await confirm_broadcast(message=msg, bot=bot, chat_id=chat_id, message_id=message_id, reply_markup=added_kb)


async def confirm_broadcast(
    message: Message, bot: Bot, message_id: int, chat_id: int, reply_markup: InlineKeyboardMarkup = None
):
    await bot.copy_message(chat_id, chat_id, message_id, reply_markup=reply_markup)
    await message.answer(
        _("Вот сообщение, которое будет отправлено! Подтвердите рассылку!"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=_("Подтвердить"), callback_data="confirm_broadcast"),
                ],
                [
                    InlineKeyboardButton(text=_("Отклонить"), callback_data="cancel_broadcast"),
                ],
            ]
        ),
    )


async def sender_decide(call: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    int(data.get("message_id"))
    int(data.get("chat_id"))
    data.get("button_text")
    data.get("button_url")
    data.get("camp_name")
    data.get("camp_message")

    if call.data == "confirm_broadcast":
        await call.message.edit_text(text=_("Начинаю рассылку!"), reply_markup=None)
    elif call.data == "cancel_broadcast":
        await call.message.edit_text(text=_("Рассылка отменена"), reply_markup=None)

    await state.clear()


@router.message(Command(commands=["backup"]))
@router.message(F.text == __("📦 Резервная копия БД"))
async def admin_backup_handler(msg: Message, bot: Bot):
    await msg.answer(_("Начинаю создание копии БД..."))
    try:
        with zipfile.ZipFile(
            f"backup_{datetime.datetime.now().strftime('%Y-%d-%m')}.zip", "w", compression=zipfile.ZIP_DEFLATED
        ) as zip_file:
            zip_file.write("database.db")
            zip_file.comment = b"{date}".replace(
                b"{date}", bytes(f'Резервная копия от: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}', "utf-8")
            )

        await bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.UPLOAD_DOCUMENT)
        await bot.send_document(
            chat_id=msg.chat.id,
            document=FSInputFile(path=f"backup_{datetime.datetime.now().strftime('%Y-%d-%m')}.zip"),
            caption=_("Резервная копия БД от {date}").format(date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M")),
        )
        os.remove(f"backup_{datetime.datetime.now().strftime('%Y-%d-%m')}.zip")
    except Exception as e:
        os.remove(f"backup_{datetime.datetime.now().strftime('%Y-%d-%m')}.zip")
        loguru.logger.error(f"Не удалось создать копию БД\n\n{e}")
        await msg.answer(_("Не удалось создать копию БД. Возможно файл слишком большой! Проверьте логи!"))
