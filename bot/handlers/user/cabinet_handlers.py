import json
import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile

from api.iIkoCloud.enums import TypeRCI
from api.iIkoCloud.iIkoCloud import IikoCloudAPI
from bot.mics.helpers.Config import Config

router: Router = Router()
iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get('IIKOCLOUD_LOGIN'))


# TODO: Проверить, что пользователь авторизован
@router.message(F.text == 'Бонусная карта')
async def profile_handler(msg: Message):
    # TODO: Сделать генерацию и вывод QR кода

    # TODO: Сделать dataclass с парамтерами профиля
    # TODO: Получить с БД номер телефона пользователя
    profile_info = iiko.customer_info(
        organization_id=Config.get('IIKOCLOUD_ORGANIZATIONS_IDS', 'list')[0],
        identifier='79130478769',
        type=TypeRCI.phone
    )

    bot = msg.bot

    import qrcode

    info = (f'Номер бонусной карты: {profile_info["phone"]}\n\n'
            f'Бонусов: {round(profile_info["walletBalances"][0]["balance"])}')

    text = "79130478769"

    # Создание QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr_code.png")

    photo = FSInputFile('qr_code.png')

    await msg.answer(info)
    await bot.send_photo(chat_id=msg.chat.id, photo=photo, caption=info)

    os.remove('qr_code.png')

    await msg.answer(text='Успей потратить!')

