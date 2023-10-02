from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from bot.states.admin.BroadcastStates import BroadcastStates


async def get_sender(msg: Message, command: CommandObject, state: FSMContext):
    if not command.args:
        await msg.answer(_("Для создания новой рассылки введите команду /sender <имя рассылки>"))
        return
    await msg.answer(
        _("Приступаю к созданию новой рассылки!" "Название рассылки: <b>{broadcatst_name}</b>").format(
            broadcatst_name=command.args
        )
    )

    await state.update_data(broadcatst_name=command.args)
    await state.set_state(BroadcastStates.get_messages)
