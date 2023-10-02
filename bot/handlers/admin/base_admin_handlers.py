from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

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
            ┗ Заблокировало <b>бота</b>: <code>{bot_blocked_count}</code>

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
            reviews_total=stats.get("total_reviews"),
            reviews_order_positive=stats.get("reviews_order_positive"),
            reviews_order_negative=stats.get("reviews_order_negative"),
            reviews_service_negative=stats.get("reviews_service_negative"),
            reviews_positive=stats.get("total_positive_reviews"),
            reviews_negative=stats.get("total_negative_reviews"),
            reviews_avg_order_rating=stats.get("reviews_avg_order_rating"),
            reviews_avg_service_rating=stats.get("reviews_avg_service_rating"),
            income_today=stats.get("income_today"),
            income_week=stats.get("income_week"),
            income_month=stats.get("income_month"),
            income_all_time=stats.get("income_all_time"),
            bot_blocked_count=stats.get("bot_blocked"),
        )
    )

    await msg.answer(message, parse_mode="HTML")


@router.message(Command(commands=["admin", "ap", "admin_panel"]))
async def admin_panel_handler(msg: Message):
    await msg.answer(
        _("Добро пожаловать в панель управления, <b>{user}</b>!").format(user=msg.from_user.full_name),
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
async def add_button_handler(call: CallbackQuery, state: FSMContext):
    if call.data == "add_button":
        await state.set_state(BroadcastStates.button_url)
        await call.message.answer(text=_("Отправьте текст для кнопки!"), reply_markup=None)
    elif call.data == "no_button":
        await call.message.edit_reply_markup(reply_markup=None)

    await call.answer()


@router.message(BroadcastStates.button_url)
async def button_url_handler(msg: Message, state: FSMContext):
    await state.update_data(button_text=msg.text)
    await msg.answer("Введите ссылку для кнопки")
    data = await state.get_data()
    print("Данные, которые ввели:", data)
