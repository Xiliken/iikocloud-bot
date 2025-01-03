import hashlib
from datetime import date, datetime, timedelta
from typing import Optional, Union

import loguru
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
        self._domain = f"{domain}/resto/api"
        self._token: Optional[str] = None
        self._time_token: Optional[date] = None
        self._set_token(working_token) if working_token is not None else self._get_access_token()
        self._last_data = None
        self._headers = {"Content-Type": "application/json", "Timeout": "45"} if base_headers is None else base_headers

    def __del__(self):
        loguru.logger.info(f"Уничтожен экземпляр класса {self.__class__.__name__}")
        self._quit_token()

    def check_status_code_token(self, code: Union[str, int]):
        if str(code) == "401":
            self._get_access_token()
        elif str(code) == "400":
            pass
        elif str(code) == "403":
            loguru.logger.error("Что-то пошло не так при получении токена. Смотри логи. Пытаюсь разлогиниться.")
            self._quit_token()
        elif str(code) == "408":
            pass
        elif str(code) == "500":
            pass

    def check_token_time(self) -> bool:
        """
        Проверка на время жизни токена.
        :return: Если прошло 60 минут, будет запрощен токен, и метод вернет True,иначе вернется False
        """
        one_hour_ago = datetime.now() - timedelta(hours=1)
        time_token = self._time_token

        if self._token is not None:
            try:
                if time_token <= one_hour_ago:
                    self._quit_token()
                    self.access_token()
                    loguru.logger.info(f"Получен новый токен для IikoServer: {self._token}")
                    return True
                else:
                    return False
            except TypeError:
                raise CheckTimeToken(
                    self.__class__.__qualname__,
                    self.check_token_time.__name__,
                    f"Не смог запросить или обновить токен!",
                )
        else:
            return False

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
            self.check_token_time()
            result = self._session.get(
                f"{self._domain}/auth?login={self._login}&pass={hashlib.sha1(self._password.encode()).hexdigest()}",
                timeout=self.DEFAULT_TIMEOUT,
            )

            if result.text is not None and "License enhancement is required" in result.text:
                self._quit_token()

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

    def _quit_token(self):
        """
        Уничтожение токена
        """
        try:
            result = self.session_s.get(url=f"{self.domain}/logout?key={self._token}", timeout=self.DEFAULT_TIMEOUT)
            if result.status_code == 200:
                loguru.logger.debug(f"Токен {self._token} уничтожен")
                # self.access_token()
            return result.text
        except requests.exceptions.ConnectTimeout:
            loguru.logger.error("Не удалось подключиться к серверу IikoServer")
        except Exception as e:
            loguru.logger.error(f"Не удалось подключиться к серверу IikoServer\n{e}")

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
            loguru.logger.debug(f"Текущий токен при получении подразделений {self._token}")
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
            loguru.logger.debug(f"Текущий токен при получении доходов: {self._token}")
            return requests.get(
                url=self._domain + f"/reports/sales?key={self._token}&department={department}",
                params=data,
                timeout=self.DEFAULT_TIMEOUT,
            ).content
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(f"Не удалось получить выручку: \n{err}")
        except TypeError as err:
            raise TypeError(f"Не удалось получить выручку: \n{err}")
