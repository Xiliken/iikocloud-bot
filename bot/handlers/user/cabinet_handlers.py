import json
import os

from PIL import Image
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from api.iIkoCloud.enums import TypeRCI
from api.iIkoCloud.iIkoCloud import IikoCloudAPI
from bot.database.models.User import User
from bot.keyboards.inline import sell_inline_kb
from bot.mics.helpers.Config import Config
from utils.main import generate_qr

router: Router = Router()
iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get('IIKOCLOUD_LOGIN'))


# TODO: Проверить, что пользователь авторизован
@router.message(F.text == 'Бонусная карта')
async def profile_handler(msg: Message, session: AsyncSession):
    # TODO: Сделать dataclass с парамтерами профиля
    bot = msg.bot

    if await session.scalar(exists().where(User.user_id == msg.from_user.id).select()):
        user = await session.scalars(select(User).where(User.user_id == msg.from_user.id))
        user = user.first()

        profile_info = iiko.customer_info(
            organization_id=Config.get('IIKOCLOUD_ORGANIZATIONS_IDS', 'list')[0],
            identifier=user.phone_number,
            type=TypeRCI.phone
        )

        generate_qr(text=user.phone_number, use_logo=False)

        photo = FSInputFile('qr_code.png')

        info = (f'Номер бонусной карты: {profile_info["phone"]}\n\n'
                f'Бонусов: {round(profile_info["walletBalances"][0]["balance"])}')

        await bot.send_photo(chat_id=msg.chat.id, photo=photo, caption=info, reply_markup=sell_inline_kb())

        os.remove('qr_code.png')
