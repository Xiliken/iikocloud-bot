from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from bot.fitlers import IsAdmin
from bot.keyboards.admin.inline_admin import admin_report_ikb
from bot.keyboards.admin.reply_admin import admin_main_kb
from bot.mics.const_functions import clear_text

router: Router = Router()
router.message.filter(IsAdmin())


@router.message(Command(commands=["stats"]))
@router.message(F.text == __("📊 Статистика"))
async def admin_stats_handler(msg: Message):
    message = clear_text(
        _(
            """
    <b>📊 СТАТИСТИКА БОТА</b>
    ➖➖➖➖➖➖➖➖➖➖
    <b>👤 Пользователи</b>
    ┣ Регистраций за <b>День</b>: {reg_day_count}
    ┣ Регистраций за <b>Неделю</b>: {reg_week_count}
    ┣ Регистраций за <b>Месяц</b>: {reg_month_count}
    ┗ Регистраций за <b>Все время</b>: {reg_all_time_count}

    <b> ⭐️ СТАТИСТИКА ОТЗЫВОВ:</b>
    ┣ Отзывов за все время: {reviews_count}
    ┣ Положительных: {reviews_positive}
    ┗ Отрицательных: {reviews_negative}

    <b> 💰 СТАТИСТИКА ДОХОДА:</b>
    ┣ Доход за сегодня: {income_today}
    ┣ Доход за неделю: {income_week}
    ┣ Доход за месяц: {income_month}
    ┗ Доход за всё время: {income_all_time}
"""
        )
    )

    await msg.answer(message, parse_mode="HTML", reply_markup=admin_report_ikb())


@router.message(Command(commands=["admin", "ap", "admin_panel"]))
async def admin_panel_handler(msg: Message):
    await msg.answer(
        _("Добро пожаловать в панель управления, <b>{user}</b>!").format(
            user=msg.from_user.full_name
        ),
        reply_markup=admin_main_kb(),
    )
