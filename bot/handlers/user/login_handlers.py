import random

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import bot.mics.iikoapi
from api.iIkoCloud.enums import TypeRCI
from api.iIkoCloud.iIkoCloud import IikoCloudAPI
from bot.database.models.User import User
from bot.fitlers import IsPhoneNumber
from bot.keyboards.reply import cancel_kb, auth_kb
from bot.mics.helpers.Config import Config
from bot.states.user.LoginStates import LoginStates

router: Router = Router()
iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get('IIKOCLOUD_LOGIN'))

MAX_SMS_ATTEMPTS = 3
attempts = {}  # Количество попыток ввода кода
verification_code = random.randint(1000, 9999)


@router.message(Command(commands=['login']), StateFilter(default_state))
@router.message(F.text == '🔑 Авторизация', StateFilter(default_state))
async def login_step_one(msg: Message, state: FSMContext) -> None:
    await msg.answer(text='Пожалуйста, введите номер телефона', reply_markup=cancel_kb())
    await state.set_state(LoginStates.phone_number)


@router.message(StateFilter(LoginStates.phone_number), IsPhoneNumber())
async def login_step_phone_number(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    # Проверить, есть ли такой номер в iko
    iiko_user = iiko.customer_info(organization_id=Config.get('IIKOCLOUD_ORGANIZATIONS_IDS', 'list')[0],
                                   type=TypeRCI.phone,
                                   identifier=msg.text,
                                   )

    if bot.mics.iikoapi.check_user_exists(iiko_user):
        # Пользователь существует в iko, на всякий случай добавить его в БД и отправить СМС
        sql = await session.execute(select(User).where(User.user_id == msg.from_user.id and User.phone_number != msg.text))

        if sql.scalar():
            await msg.answer('Извините, но данный аккаунт Telegram привязан к другому номеру телефона!', reply_markup=auth_kb())
            await state.clear()
            return

        else:
            await session.merge(User(user_id=msg.from_user.id, phone_number=msg.text, is_admin=False))
            await msg.answer('На указанный номер отправлен код с подтверждением авторизации!')

        #SMSC().send_sms()
        await session.commit()
    else:
        # Пользователя не существует
        await state.clear()
        await msg.answer(f'Извините, не удалось найти пользователя с номером +{msg.text}\n\n'
                         f'Пожалуйста, проверьте корректность введенного номера, или зарегистрируйте новый аккаунт!',
                         reply_markup=auth_kb())
