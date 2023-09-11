from typing import Optional

from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import ImageColorMask, RadialGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer


def generate_qr(text: str, use_logo: Optional[bool] = False) -> None:
    from PIL import Image
    import qrcode

    # Создаем QR code
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=3,
    )

    qr.add_data(text)
    img = qr.make(fit=False)

    # Создание изображения
    if use_logo:
        qr_img = qr.make_image()

        # Открываем логотип
        logo = Image.open('logo.png')

        # Масштабируйте логотип до указанного размера
        logo_x_position = (qr_img.size[0] - logo.size[0]) // 2
        logo_y_position = (qr_img.size[1] - logo.size[1]) // 2
        logo_position = (logo_x_position, logo_y_position)

        # Наложите логотип на QR-код
        #qr_img.paste(logo, logo_position)

        qr_img.save('qr_code.png')
    else:
        img = qr.make_image(fill_color="black", back_color="white")
        img.save('qr_code.png')

