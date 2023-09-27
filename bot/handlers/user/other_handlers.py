import aiogram
import loguru
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import (
    KICKED,
    MEMBER,
    ChatMemberUpdatedFilter,
    Command,
    StateFilter,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks.RateCallbackData import RateCallbackData, RateServiceCallbackData
from bot.database.models import User
from bot.fitlers.IsAuth import IsAuth
from bot.keyboards import cabinet_main_kb
from bot.keyboards.inline import rate_last_order_ikb, rate_last_service
from bot.mics import Config, normalize_phone_number, notify

router: Router = Router()


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands=["cancel"]), StateFilter(default_state))
@router.message(F.text == __("❌ Отмена"), StateFilter(default_state))
async def cancel_handler_default_state(msg: Message) -> None:
    await msg.answer(
        text=_("Нечего отменять"), reply_markup=aiogram.types.ReplyKeyboardRemove()
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands=["cancel"]), ~StateFilter(default_state))
@router.message(F.text == __("❌ Отмена"), ~StateFilter(default_state))
async def cancel_handler(msg: Message, state: FSMContext) -> None:
    await msg.answer(
        text=_("Действие успешно отменено"),
        reply_markup=aiogram.types.ReplyKeyboardRemove(),
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


@router.message(F.text == __("⬅️ В главное меню"), StateFilter(default_state), IsAuth())
async def main_menu_handler(msg: Message) -> None:
    await msg.delete()
    await msg.answer(text="⬅️ В главное меню", reply_markup=cabinet_main_kb())


# Этот хэндлер будет срабатывать на оценивание заказа от пользователя
@router.callback_query(RateCallbackData.filter())
async def rate_callback_handler(
    callback: aiogram.types.CallbackQuery,
    callback_data: RateCallbackData,
    bot: Bot,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    try:
        # Получаем пользователя из бд
        sender = await session.scalars(
            select(User).where(User.user_id == callback.from_user.id)
        )

        sender = sender.first()

        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("✉️ Написать гостю"),
                        url=f"tg://user?id={sender.user_id}",
                    )
                ]
            ]
        )

        # Проверка рейтинга заказа
        if callback_data.food_rating <= 3:
            await bot.send_message(
                chat_id=Config.get("NOTIFY_ADMIN_ID", "int"),
                text=_(
                    "Гость <b>{name}</b> (+{phone}) оценил заказ на <b>{rate}</b>"
                ).format(
                    name=callback.from_user.full_name,
                    phone=normalize_phone_number(sender.phone_number),
                    rate=callback_data.food_rating,
                ),
                reply_markup=ikb,
            )

        await callback.message.edit_text(
            text=_(
                "Пожалуйста, оцените <b><u>обслуживание</u></b> по шкале <b>от 1 до 5</b>."
                "Где 5 наивысшая оценка"
            ),
            reply_markup=rate_last_service(),
        )
    except TelegramBadRequest:
        loguru.logger.error(TelegramBadRequest)


@router.callback_query(RateServiceCallbackData.filter())
async def rate_service_callback_handler(
    callback: aiogram.types.CallbackQuery,
    callback_data: RateServiceCallbackData,
    bot: Bot,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    try:
        # Получаем пользователя из бд
        sender = await session.scalars(
            select(User).where(User.user_id == callback.from_user.id)
        )

        sender = sender.first()

        ikb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("✉️ Написать гостю"),
                        url=f"tg://user?id={sender.user_id}",
                    )
                ]
            ]
        )

        # Проверка рейтинга заказа
        if callback_data.rating <= 3:
            await bot.send_message(
                chat_id=Config.get("NOTIFY_ADMIN_ID", "int"),
                text=_(
                    "Гость <b>{name}</b> (+{phone}) оценил обслуживание на <b>{rate}</b>"
                ).format(
                    name=callback.from_user.full_name,
                    phone=normalize_phone_number(sender.phone_number),
                    rate=callback_data.rating,
                ),
                reply_markup=ikb,
            )

        await callback.message.edit_text(_("Спасибо за ваш отзыв! Ждем Вас снова!"))

    except TelegramBadRequest:
        loguru.logger.error(TelegramBadRequest)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, session: AsyncSession):
    # Установить статус, что бот заблокирован
    await session.execute(
        update(User).where(User.user_id == event.from_user.id).values(is_blocked=True)
    )
    await session.commit()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated, session: AsyncSession):
    # Установить статус, что бот разблокирован
    await session.execute(
        update(User).where(User.user_id == event.from_user.id).values(is_blocked=False)
    )
    await session.commit()


# @router.message(StateFilter(default_state))
# async def send_message(msg: Message) -> None:
#     await msg.answer(f"Простите, но мой интеллект еще не настолько умен, чтобы общаться с вами на любые темы! ☹️\n"
#                      f"Пожалуйста, для общения со мной, используйте команды или меню ниже! 🤗")
