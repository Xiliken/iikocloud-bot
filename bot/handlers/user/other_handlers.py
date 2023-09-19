import aiogram
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

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


# @router.message(StateFilter(default_state))
# async def send_message(msg: Message) -> None:
#     await msg.answer(f"Простите, но мой интеллект еще не настолько умен, чтобы общаться с вами на любые темы! ☹️\n"
#                      f"Пожалуйста, для общения со мной, используйте команды или меню ниже! 🤗")
