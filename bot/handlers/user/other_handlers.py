from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram import F

router: Router = Router()


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands=['cancel']), StateFilter(default_state))
@router.message(F.text == '❌ Отмена', StateFilter(default_state))
async def cancel_handler_default_state(msg: Message) -> None:
    await msg.answer(text='Нечего отменять')


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands=['cancel']), ~StateFilter(default_state))
@router.message(F.text == '❌ Отмена', ~StateFilter(default_state))
async def cancel_handler(msg: Message, state: FSMContext) -> None:
    await msg.answer(text='Действите успешно отменено')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()