from datetime import datetime, timedelta, date
from typing import Optional, Union

import requests
import json

from requests import Response

from api.iIkoCloud.exceptions import CheckTimeToken, SetSession, TokenException
from api.iIkoCloud.models import CustomErrorModel, BaseOrganizationsModel


class IiKoCloud:
    """Класс для работы с API IikoCloud"""

    DEFAULT_TIMEOUT = 15

    # __BASE_URL = "https://api-ru.iiko.services"

    def __int__(self,
                api_login: str,
                session: Optional[requests.Session] = None,
                debug: bool = False,
                base_url: str = None,
                working_token: str = None,
                base_headers: dict = None,
                ):

        """
            :param api_login: Логин авторизации
            :param session: Объект сессии
            :param debug: Режим отладки
            :param base_url: URL IikoCloud API
            :param working_token: Инициализировать объект на основе рабочего токена, то есть не запрашивая новый
            :param base_headers: Базовые заголовки запроса для IikoCloud API
        """

        # Установка сессии
        if session is not None:
            self.__session = session
        else:
            self.__session = requests.Session()

        self.__api_login = api_login
        self.__token: Optional[str] = None
        self.__debug = debug
        self.__time_token: Optional[date] = None
        self.__organizations_ids: Optional[list[str]] = None
        self.__strfdt = "%Y-%m-%d %H:%M:%S.000"
        self.__base_url = "https://api-ru.iiko.services" if base_url is None else base_url
        self.__headers = \
            {
                "Content-Type": "application/json",
                "Timeout": "45"
            } if base_headers is None else base_headers
        self.__set_token(working_token) if working_token is not None else self.__get_access_token()

    def check_status_code_token(self, code: Union[str, int]):
        if str(code) == "401":
            self.__get_access_token()
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
        time_token = self.__time_token

        try:
            if time_token <= fifteen_minutes_ago:
                self.__get_access_token()
                return True
            else:
                return False
        except TypeError:
            raise CheckTimeToken(
                self.__class__.__qualname__,
                self.check_token_time.__name__,
                f"Не смог запросить или обновить токен!"
            )

    @property
    def api_login(self) -> str:
        return self.__api_login

    @property
    def token(self) -> str:
        return self.__token

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, value: str):
        self.__base_url = value

    @property
    def strfdt(self):
        return self.__strfdt

    @strfdt.setter
    def strfdt(self, value: str):
        self.__strfdt = value

    @property
    def session_s(self) -> requests.Session:
        """Вывести сессию"""
        return self.__session

    @session_s.setter
    def session_s(self, session: requests.Session = None):
        """Изменение сессии"""
        if session is None:
            raise SetSession(
                self.__class__.__qualname__,
                self.session_s.__name__,
                f"Не присвоен объект типа requests.Session")
        else:
            self.__session = session

    @property
    def headers(self):
        return self.__headers

    @property
    def time_token(self):
        return self.__time_token

    @headers.setter
    def headers(self, value: str):
        self.__headers = value

    def get_token(self) -> str:
        pass

    def access_token(self):
        """Получить токен доступа"""
        data = json.dumps({"apiLogin": self.api_login})
        try:
            result = requests.post(f'{self.__base_url}/api/1/access_token', json=data)

            response_data: dict = json.loads(result.content)

            if (response_data.get("errorDescription", None)) is not None:
                raise TypeError(f'{response_data}')

            if response_data.get("token", None) is not None:
                self.check_status_code_token(result.status_code)
                self.__set_token(response_data.get("token", ""))
        except requests.exceptions.RequestException as err:
            raise TokenException(self.__class__.__qualname__,
                                 self.access_token.__name__,
                                 f"Не удалось получить токен доступа:\n {err}")
        except TypeError as err:
            raise TokenException(self.__class__.__qualname__,
                                 self.access_token.__name__,
                                 f"Не удалось получить токен доступа:\n {err}")

    def __get_access_token(self):
        out = self.access_token()
        if isinstance(out, CustomErrorModel):
            raise TokenException(self.__class__.__qualname__,
                                 self.access_token.__name__,
                                 f"Не удалось получить токен доступа: \n{out}")

    def __set_token(self, token):
        self.__token = token
        self.__headers["Authorization"] = f"Bearer {self.token}"
        self.__time_token = datetime.now()

    def organizations(self, organizations_ids: list[str] = None, timeout=DEFAULT_TIMEOUT) -> Response:
        """
        Возвращает список организаций
        :param organizations_ids:
        :param timeout:
        :return:
        """

        data = {}

        if organizations_ids is not None:
            data['organizationIds'] = organizations_ids

        try:
            response_data = requests.post(
                url=f"{self.__base_url}/api/1/organizations",
                data=json.dumps(data)
            )

            return response_data

        except requests.exceptions.RequestException as err:
            raise TokenException(self.__class__.__qualname__,
                                 self.organizations.__name__,
                                 f"Не удалось получить организации: \n{err}")
        except TypeError as err:
            raise TypeError(self.__class__.__qualname__,
                            self.organizations.__name__,
                            f"Не удалось получить организации: \n{err}")


