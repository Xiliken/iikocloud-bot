import hashlib
from datetime import date, datetime, timedelta
from typing import Optional, Union

import requests

from services.iikocloud.models import CustomErrorModel
from services.iikoserver.exceptions import CheckTimeToken, SetSession, TokenException


class IikoServer:
    """Класс для работы с IikoServer"""

    DEFAULT_TIMEOUT = 15

    def __init__(
        self,
        domain: str = None,
        login: str = None,
        password: str = None,
        working_token: str = None,
        session: Optional[requests.Session] = None,
        base_headers: dict = None,
    ):
        # Установка сессии
        if session is not None:
            self._session = session
        else:
            self._session = requests.Session()

        self._login = login
        self._password = password
        self._domain = domain + "/resto/api"
        self._token: Optional[str] = None
        self._time_token: Optional[date] = None
        self._set_token(working_token) if working_token is not None else self._get_access_token()
        self._last_data = None
        self._headers = {"Content-Type": "application/json", "Timeout": "45"} if base_headers is None else base_headers

    def check_status_code_token(self, code: Union[str, int]):
        if str(code) == "401":
            self._get_access_token()
        elif str(code) == "400":
            pass
        elif str(code) == "408":
            pass
        elif str(code) == "500":
            pass

    def check_token_time(self) -> bool:
        """
        Проверка на время жизни токена.
        :return: Если прошло 15 минут, будет запрощен токен, и метод вернет True,иначе вернется False
        """
        fifteen_minutes_ago = datetime.now() - timedelta(minutes=15)
        time_token = self._time_token

        try:
            if time_token <= fifteen_minutes_ago:
                self._get_access_token()
                return True
            else:
                return False
        except TypeError:
            raise CheckTimeToken(
                self.__class__.__qualname__,
                self.check_token_time.__name__,
                f"Не смог запросить или обновить токен!",
            )

    @property
    def login(self):
        return self._login

    @property
    def password(self):
        return self._password

    @property
    def token(self):
        return self._token

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value: str):
        self._domain = value

    @property
    def session_s(self) -> requests.Session:
        """Вывести сессию"""
        return self._session

    @session_s.setter
    def session_s(self, session: requests.Session = None):
        """Изменение сессии"""
        if session is None:
            raise SetSession(
                self.__class__.__qualname__,
                self.session_s.__name__,
                f"Не присвоен объект типа requests.Session",
            )
        else:
            self._session = session

    @property
    def time_token(self):
        return self._time_token

    @property
    def timeout(self):
        return self._headers.get("Timeout")

    @timeout.setter
    def timeout(self, value: int):
        self._headers.update({"Timeout": str(value)})

    @timeout.deleter
    def timeout(self):
        self._headers.update({"Timeout": str(self.DEFAULT_TIMEOUT)})

    def access_token(self):
        try:
            result = self._session.get(
                f"{self._domain}/auth?login={self._login}&pass={hashlib.sha1(self._password.encode()).hexdigest()}",
                timeout=self.DEFAULT_TIMEOUT,
            )

            if (
                result.text is not None
                and "Неверный пароль для пользователя" not in result.text
                and "Пользователь с логином" not in result.text
            ):
                self.check_status_code_token(result.status_code)
                self._set_token(result.text)

            return result.text
        except Exception as e:
            raise Exception("Ошибка при обновлении токена доступа IikoServer:\n ", e)

    def _get_access_token(self):
        out = self.access_token()
        if isinstance(out, CustomErrorModel):
            raise TokenException(
                self.__class__.__qualname__,
                self.access_token.__name__,
                f"Не удалось получить токен доступа: \n{out}",
            )

    def _set_token(self, token):
        self._token = token
        self._time_token = datetime.now()

    def _get_request(self, url: str, params: dict = None, timeout=DEFAULT_TIMEOUT):
        if params is None:
            params = {}
        if timeout != self.DEFAULT_TIMEOUT:
            self.timeout = timeout

        response = self.session_s.get(url=f"{self.domain}{url}", params=params)

        if response.status_code == 401:
            self._get_access_token()
            return self._get_request(url=url, params=params, timeout=timeout)

        response_data = response.text

        self._last_data = response_data
        del self.timeout

        return response_data

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
                self._domain
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
            logout = requests.get(self._domain + "/logout?key=" + self._token)
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
            urls = self._domain + "/corporation/departments?key=" + self._token
            return self._get_request(url="/corporation/departments?key=" + self._token, timeout=self.DEFAULT_TIMEOUT)
            # return requests.get(url=urls, timeout=self.DEFAULT_TIMEOUT).content
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException("Ошибка получения списка отделов:\n", e)
        except Exception as e:
            raise Exception("Ошибка получения списка отделов:\n\n", e)

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
                url=self._domain + f"/reports/sales?key={self._token}&department={department}",
                params=data,
                timeout=self.DEFAULT_TIMEOUT,
            ).content
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(f"Не удалось получить выручку: \n{err}")
        except TypeError as err:
            raise TypeError(f"Не удалось получить выручку: \n{err}")
