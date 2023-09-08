from datetime import datetime
from time import sleep
import smtplib
from typing import Optional

import requests

from bot.mics.helpers.Config import Config

try:
    from urllib import urlopen, quote
except ImportError:
    from urllib.request import urlopen
    from urllib.parse import quote

# Константы для настройки библиотеки
SMSC_LOGIN = Config.get('SMSC_LOGIN')  # логин клиента
SMSC_PASSWORD = Config.get('SMSC_PASSWORD')  # пароль
SMSC_POST = Config.get('SMSC_POST', 'bool')  # использовать метод POST
SMSC_HTTPS = Config.get('SMSC_HTTPS', 'bool')  # использовать HTTPS протокол
SMSC_CHARSET = Config.get('SMSC_CHARSET')  # кодировка сообщения (windows-1251 или koi8-r), по умолчанию используется utf-8
SMSC_DEBUG = Config.get('SMSC_DEBUG', 'bool')  # флаг отладки

# Константы для отправки SMS по SMTP
SMSC_SMTP_FROM = Config.get('SMSC_SMTP_FROM')  # e-mail адрес отправителя
SMSC_SMTP_SERVER = Config.get('SMSC_SMTP_SERVER')  # адрес smtp сервера
SMSC_SMTP_LOGIN = Config.get('SMSC_SMTP_LOGIN')  # логин для smtp сервера
SMSC_SMTP_PASSWORD = Config.get('SMSC_SMTP_PASSWORD')  # пароль для smtp сервера


class SMSC(object):
    def send_sms(
            self,
            phones,
            message: str,
            translit: Optional[int] = 0,
            time: Optional[str] = '',
            id: Optional[int] = None,
            format: Optional[int] = 0,
            sender: Optional[bool] = False,
            query: Optional[str] = ''
    ):
        formats = ["flash=1", "push=1", "hlr=1", "bin=1", "bin=2", "ping=1", "mms=1", "mail=1", "call=1", "viber=1",
                   "soc=1"]

        format_param = formats[format - 1] if format > 0 else ""
        sender_param = f"&sender={quote(str(sender))}" if sender else ""
        time_param = f"&time={quote(time)}" if time else ""
        query_param = f"&{query}" if query else ""

        params = {
            "cost": 3,
            "phones": quote(phones),
            "mes": message,
            "translit": translit,
            "id": id,
            "format": format_param,
            "sender": sender_param,
            "time": time_param,
        }

        param_string = "&".join(f"{key}={value}" for key, value in params.items())

        m = self._smsc_send_cmd("send", param_string + query_param)


        # Обработка результата
        if SMSC_DEBUG:
            if m[1] > "0":
                print(
                    f"Сообщение отправлено успешно. ID: {m[0]}, всего SMS: {m[1]}, стоимость: {m[2]}, баланс: {m[3]}"
                )
            else:
                error_message = f"Ошибка №{m[1][1:]}"
                if m[0] > "0":
                    error_message += f", ID: {m[0]}"
                print(error_message)

        return m

    def get_balance(self):
        m = self._smsc_send_cmd("balance")  # (balance) или (0, -error)

        if SMSC_DEBUG:
            message = "Сумма на счете: " + m[0] if len(m) < 2 else "Ошибка №" + m[1][1:]
            print(message)

        return m[0] if len(m) > 1 else False

    def _smsc_send_cmd(self, cmd, arg=""):
        # URL для запросов
        base_url = f"https://smsc.ru/sys/{cmd}.php"

        # Формирование параметров запроса

        params = {
            "login": SMSC_LOGIN,
            "psw": SMSC_PASSWORD,
            "fmt": "1",
            "charset": SMSC_CHARSET,
        }

        arg_dict = dict(item.split("=") for item in arg.split("&"))

        res = params.update(arg_dict)

        ret = ""
        max_attempts = 5

        for i in range(max_attempts):
            try:
                # Выполнение HTTP-запроса
                response = requests.get(base_url, params=params)
                response.raise_for_status()

                # Получение и декодирование ответа
                ret = response.text
                break  # Выход из цикла при успешном запросе
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при выполнении запроса: {e}")
                ret = ""

        if ret == "":
            if SMSC_DEBUG:
                print("Ошибка чтения адреса: " + base_url)
            ret = ","  # Фиктивный ответ

        return ret.split(",")
