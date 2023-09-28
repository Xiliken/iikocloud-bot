from aiogram import F, Router
from aiogram.filters import Command
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

            <b>👤 ПОЛЬЗОВАТЕЛИ</b>
            ┣ Регистраций за <b>День</b>: <code>{reg_day_count}</code>
            ┣ Регистраций за <b>Неделю</b>: <code>{reg_week_count}</code>
            ┣ Регистраций за <b>Месяц</b>: <code>{reg_month_count}</code>
            ┣ Регистраций за <b>Все время</b>: <code>{reg_all_time_count}</code>
            ┗ Заблокировало бота: <code>{bot_blocked_count}</code>

            <b> ⭐️ ОТЗЫВЫ</b>
            ┣ Отзывов за <b>все время</b>: <code>{reviews_total}</code>
            ┣ 😻 Положительных: <code>{reviews_positive}</code>
            ┣ 😡 Отрицательных: <code>{reviews_negative}</code>
            ╰┈➤ <b><u>ЗАКАЗЫ</u></b>
            ┣ 😻 Положительных: <code>{reviews_order_positive}</code>
            ┣ 😡 Отрицательных: <code>{reviews_order_negative}</code>
            ┣ 🤔 Средняя оценка: <code>{reviews_avg_order_rating}</code>
            ╰┈➤ <b><u>ОБСЛУЖИВАНИЕ</u></b>
            ┣ 😻 Положительных: <code>{reviews_service_negative}</code>
            ┣ 😡 Отрицательных: <code>{reviews_service_negative}</code>
            ┗ 🤔 Средняя оценка: <code>{reviews_avg_service_rating}</code>

            <b> 💰 ДОХОД</b>
            ┣ Доход за <b>сегодня</b>: <code>{income_today}</code>
            ┣ Доход за <b>неделю</b>: <code>{income_week}</code>
            ┣ Доход за <b>месяц</b>: <code>{income_month}</code>
            ┗ Доход за <b>всё время</b>: <code>{income_all_time}</code>
        """
        ).format(
            reg_day_count=stats.get("reg_users_today"),
            reg_week_count=stats.get("reg_users_week"),
            reg_month_count=stats.get("reg_users_month"),
            reg_all_time_count=stats.get("reg_users_all"),
            reviews_total=stats.get("reviews_total"),
            reviews_order_positive=stats.get("reviews_order_positive"),
            reviews_order_negative=stats.get("reviews_order_negative"),
            reviews_service_negative=stats.get("reviews_service_negative"),
            reviews_positive=stats.get("reviews_positive"),
            reviews_negative=stats.get("reviews_negative"),
            reviews_avg_order_rating=stats.get("reviews_avg_order_rating"),
            reviews_avg_service_rating=stats.get("reviews_avg_service_rating"),
            income_today=stats.get("income_today"),
            income_week=stats.get("income_week"),
            income_month=stats.get("income_month"),
            income_all_time=stats.get("income_all_time"),
            bot_blocked_count=stats.get("bot_blocked"),
        )
    )

    await msg.answer(message, parse_mode="HTML", reply_markup=admin_report_ikb())


@router.message(Command(commands=["admin", "ap", "admin_panel"]))
async def admin_panel_handler(msg: Message):
    await msg.answer(
        _("Добро пожаловать в панель управления, <b>{user}</b>!").format(user=msg.from_user.full_name),
        reply_markup=admin_main_kb(),
    )
