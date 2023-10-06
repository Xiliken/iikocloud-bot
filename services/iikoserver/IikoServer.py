import hashlib
from datetime import datetime
from typing import Optional, Union

import requests


class IikoServer:
    """Класс для работы с IikoServer"""

    DEFAULT_TIMEOUT = 4

    def __init__(self, domain: str = None, login: str = None, password: str = None, token: str = None):
        self._login = login
        self._password = password
        self._base_url = domain + "/resto/api"
        self._token = token or self.get_token()

    def token(self):
        return self._token

    def get_token(self):
        """
        Метод получения нового токена
        при авторизации вы занимаете один слот лицензии. Token,
        который вы получаете при авторизации, можно использовать до того момента,
        пока он не протухнет (не перестанет работать). И если у вас только одна
        лицензия сервера, а вы уже получили token, следующее обращение к серверу за
        token-ом вызовет ошибку. Если вам негде хранить token при работе с сервером API,
        рекомендуем вам разлогиниться, что приводит к отпусканию лицензии.

        """

        try:
            url = (
                self._base_url
                + "/auth?login="
                + self._login
                + "&pass="
                + hashlib.sha1(self._password.encode()).hexdigest()
            )
            return requests.get(url=url, timeout=self.DEFAULT_TIMEOUT).text

        except Exception as e:
            print("Ошибка при обновлении токена доступа IikoServer:\n ", e)

    def quit_token(self):
        """
        Уничтожение токена
        """

        try:
            logout = requests.get(self._base_url + "/logout?key=" + self._token)
            print("\nТокен уничтожен: " + self._token)
            return logout

        except requests.exceptions.ConnectTimeout:
            print("Не удалось подключиться к серверу IikoServer")

    def departments(self):
        """
        Иерархия подразделений


        CORPORATION, Корпорация
        JURPERSON", Юридическое лицо
        ORGDEVELOPMENT, Структурное подразделение
        DEPARTMENT, Торговое предприятие
        MANUFACTURE, Производство
        CENTRALSTORE, Центральный склад
        CENTRALOFFICE, Центральный офис
        SALEPOINT, Точка продаж
        STORE, Склад
        """

        try:
            urls = self._base_url + "/corporation/departments?key=" + self._token
            return requests.get(url=urls, timeout=self.DEFAULT_TIMEOUT).content
        except Exception as e:
            print(e)

    def sales(
        self,
        department: str,
        date_from: Union[str, datetime],
        date_to: Optional[Union[str, datetime]] = None,
        hour_from: Optional[Union[str, datetime]] = None,
        hour_to: Optional[Union[str, datetime]] = None,
        dish_details: Optional[bool] = None,
        all_revenue: Optional[bool] = None,
    ):
        """
        Отчет по выручке
        :param department: Подразделение
        :param date_from: Начальная дата в формате DD.MM.YYYY
        :param date_to: Конечная дата в формате DD.MM.YYYY
        :param hour_from: Час начала интервала выборки в сутках (по умолчанию -1, все время), по умолчанию -1
        :param hour_to: Час окончания интервала выборки в сутках (по умолчанию -1, все время), по умолчанию -1
        :param dish_details: Включить ли разбивку по блюдам (true/false), по умолчанию false
        :param all_revenue: Фильтрация по типам оплат (true - все типы, false - только выручка), по умолчанию true
        :return:
        """

        data = {}

        if isinstance(date_from, datetime):
            data["dateFrom"] = date_to.strftime("%d.%m.%Y")
        elif isinstance(date_from, str):
            data["dateFrom"] = date_from

        if isinstance(date_to, datetime):
            data["dateTo"] = date_to.strftime("%d.%m.%Y")
        elif isinstance(date_to, str):
            data["dateTo"] = date_to

        if isinstance(hour_from, datetime):
            data["hourFrom"] = hour_from.strftime("%H")
        elif isinstance(hour_from, str):
            data["hourFrom"] = hour_from

        if isinstance(hour_to, datetime):
            data["hourTo"] = hour_to.strftime("%H")
        elif isinstance(hour_to, str):
            data["hourTo"] = hour_to

        if dish_details is not None:
            data["dishDetails"] = bool(dish_details)

        if all_revenue is not None:
            data["allRevenue"] = bool(all_revenue)

        try:
            return requests.get(
                url=self._base_url + f"/reports/sales?key={self._token}&department={department}",
                params=data,
                timeout=self.DEFAULT_TIMEOUT,
            ).content
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(f"Не удалось получить выручку: \n{err}")
        except TypeError as err:
            raise TypeError(f"Не удалось получить выручку: \n{err}")
