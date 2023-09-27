from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from bot.fitlers import IsAdmin
from bot.keyboards.admin.inline_admin import admin_report_ikb
from bot.keyboards.admin.reply_admin import admin_main_kb
from bot.mics.const_functions import clear_text, get_stats

router: Router = Router()
router.message.filter(IsAdmin())


@router.message(Command(commands=["stats"]))
@router.message(F.text == __("📊 Статистика"))
async def admin_stats_handler(msg: Message):
    stats = await get_stats()

    message = clear_text(
        _(
            """
            <b>📊 СТАТИСТИКА БОТА</b>
            ➖➖➖➖➖➖➖➖➖➖
            <b>👤 Пользователи</b>
            ┣ Регистраций за <b>День</b>: <code>{reg_day_count}</code>
            ┣ Регистраций за <b>Неделю</b>: <code>{reg_week_count}</code>
            ┣ Регистраций за <b>Месяц</b>: <code>{reg_month_count}</code>
            ┣ Регистраций за <b>Все время</b>: <code>{reg_all_time_count}</code>
            ┗ Заблокировало бота: <code>{bot_blocked_count}</code>

            <b> ⭐️ СТАТИСТИКА ОТЗЫВОВ:</b>
            ┣ Отзывов за все время: <code>{reviews_count}</code>
            ┣ Положительных: <code>{reviews_positive}</code>
            ┗ Отрицательных: <code>{reviews_negative}</code>

            <b> 💰 СТАТИСТИКА ДОХОДА:</b>
            ┣ Доход за сегодня: <code>{income_today}</code>
            ┣ Доход за неделю: <code>{income_week}</code>
            ┣ Доход за месяц: <code>{income_month}</code>
            ┗ Доход за всё время: <code>{income_all_time}</code>
        """
        ).format(
            reg_day_count=stats.get("reg_users_today"),
            reg_week_count=stats.get("reg_users_week"),
            reg_month_count=stats.get("reg_users_month"),
            reg_all_time_count=stats.get("reg_users_all"),
            reviews_count=0,
            reviews_positive=0,
            reviews_negative=0,
            income_today=0,
            income_week=0,
            income_month=0,
            income_all_time=0,
            bot_blocked_count=stats.get("bot_blocked"),
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
