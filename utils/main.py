import re
from datetime import datetime
from typing import Optional


def generate_qr(text: str, use_logo: Optional[bool] = False) -> None:
    import qrcode
    from PIL import Image

    # Создаем QR code
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        # box_size=10
    )

    QRcode.add_data(text)
    QRcode.make()

    # Создание изображения
    if use_logo:
        QRImg = QRcode.make_image().convert("RGB")

        # Открываем логотип
        logo = Image.open("logo.jpg")
        basewidth = 70

        # Масштабируем логотип
        wpercent = basewidth / float(logo.size[0])
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.LANCZOS)

        # Наложить логотип на QR-код
        pos = ((QRImg.size[0] - logo.size[0]) // 2, (QRImg.size[1] - logo.size[1]) // 2)
        QRImg.paste(logo, pos)

        QRImg.save("qr_code.png")
    else:
        qr_text = QRcode.make_image(fill_color=(0, 0, 0), back_color=(0, 0, 0))
        qr_text.save("qr_code.png")


def is_valid_date(date_str):
    # Проверяем формат даты с использованием регулярного выражения
    date_pattern = r"^\d{2}\.\d{2}.\d{4}$"
    if not re.match(date_pattern, date_str):
        return False

    # Пытаемся преобразовать строку в объект datetime
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False
