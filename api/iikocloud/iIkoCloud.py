import json
from datetime import date, datetime, timedelta
from typing import List, Optional, Union

import requests
from requests import Response

from api.iikocloud.enums import TypeRCI
from api.iikocloud.exceptions import CheckTimeToken, SetSession, TokenException
from api.iikocloud.models import CustomErrorModel


class BaseAPI:
    """Класс для работы с API IikoCloud"""

    DEFAULT_TIMEOUT = 15

    # __BASE_URL = "https://api-ru.iiko.services"

    def __init__(
        self,
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
        self.__base_url = (
            "https://api-ru.iiko.services" if base_url is None else base_url
        )
        self.__headers = (
            {"Content-Type": "application/json", "Timeout": "45"}
            if base_headers is None
            else base_headers
        )
        self.__set_token(
            working_token
        ) if working_token is not None else self.__get_access_token()
        self.__last_data = None

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
                f"Не смог запросить или обновить токен!",
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
                f"Не присвоен объект типа requests.Session",
            )
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

    @property
    def timeout(self):
        return self.__headers.get("Timeout")

    @timeout.setter
    def timeout(self, value: int):
        self.__headers.update({"Timeout": str(value)})

    @timeout.deleter
    def timeout(self):
        self.__headers.update({"Timeout": str(self.DEFAULT_TIMEOUT)})

    def get_token(self) -> str:
        pass

    def access_token(self):
        """Получить токен доступа"""
        data = json.dumps({"apiLogin": self.api_login})
        try:
            result = self.session_s.post(
                f"{self.__base_url}/api/1/access_token", json=data
            )
            # result = requests.post(f'{self.__base_url}/api/1/access_token', json=data)

            response_data: dict = json.loads(result.content)

            if (response_data.get("errorDescription", None)) is not None:
                raise TypeError(f"{response_data}")

            if response_data.get("token", None) is not None:
                self.check_status_code_token(result.status_code)
                self.__set_token(response_data.get("token", ""))
        except requests.exceptions.RequestException as err:
            raise TokenException(
                self.__class__.__qualname__,
                self.access_token.__name__,
                f"Не удалось получить токен доступа:\n {err}",
            )
        except TypeError as err:
            raise TokenException(
                self.__class__.__qualname__,
                self.access_token.__name__,
                f"Не удалось получить токен доступа:\n {err}",
            )

    def __get_access_token(self):
        out = self.access_token()
        if isinstance(out, CustomErrorModel):
            raise TokenException(
                self.__class__.__qualname__,
                self.access_token.__name__,
                f"Не удалось получить токен доступа: \n{out}",
            )

    def __set_token(self, token):
        self.__token = token
        self.__headers["Authorization"] = f"Bearer {self.token}"
        self.__time_token = datetime.now()

    def _post_request(self, url: str, data: dict = None, timeout=DEFAULT_TIMEOUT):
        if data is None:
            data = {}
        if timeout != self.DEFAULT_TIMEOUT:
            self.timeout = timeout

        response = self.session_s.post(
            url=f"{self.base_url}{url}", data=json.dumps(data), headers=self.headers
        )

        if response.status_code == 401:
            self.__get_access_token()
            return self._post_request(url=url, data=data, timeout=timeout)

        response_data: dict = json.loads(response.content)
        self.__last_data = response_data
        del self.timeout
        return response_data

    def organizations(
        self,
        organizations_ids: list[str] = None,
        return_additional_info: bool = False,
        includeDisabled: bool = False,
        timeout=DEFAULT_TIMEOUT,
    ) -> Response:
        """
        Возвращает список организаций
        :param includeDisabled:
        :param return_additional_info:
        :param organizations_ids:
        :param timeout:
        :return:
        """

        data = {}

        if organizations_ids is not None:
            data["organizationIds"] = organizations_ids
        if return_additional_info:
            data["returnAdditionalInfo"] = return_additional_info
        if includeDisabled:
            data["includeDisabled"] = includeDisabled

        try:
            response_data = self._post_request(
                url=f"/api/1/organizations", data=data, timeout=timeout
            )

            return response_data

        except requests.exceptions.RequestException as err:
            raise TokenException(
                self.__class__.__qualname__,
                self.organizations.__name__,
                f"Не удалось получить организации: \n{err}",
            )
        except TypeError as err:
            raise TypeError(
                self.__class__.__qualname__,
                self.organizations.__name__,
                f"Не удалось получить организации: \n{err}",
            )


class Customers(BaseAPI):
    def customer_info(
        self,
        organization_id: str,
        type: TypeRCI,
        identifier: str,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
    ):
        """
        Получить информацию о пользователе
        :param organization_id:  id орагнизации
        :param type: тип получения информации (телефон, почта и т.д)
        :param identifier: идентификатор
        :param timeout:
        :return:
        """

        data = {
            "organizationId": organization_id,
            "type": type.value,
        }

        if type == TypeRCI.phone:
            data[TypeRCI.phone.value] = identifier
        elif type == TypeRCI.card_track:
            data[TypeRCI.card_track.value] = identifier
        elif type == TypeRCI.card_number:
            data[TypeRCI.card_number.value] = identifier
        elif type == TypeRCI.email:
            data[TypeRCI.email.value] = identifier
        elif type == TypeRCI.id:
            data[TypeRCI.id.value] = identifier

        try:
            response_data = self._post_request(
                url=f"/api/1/loyalty/iiko/customer/info", data=data, timeout=timeout
            )

            return response_data

        except requests.exceptions.RequestException as err:
            raise Exception(f"Ошибка получения информации о пользователе!\n\n\n{err}")
        except TypeError as err:
            raise TypeError(f"{err}")

    def create_or_update_customer(
        self,
        organization_id: str,
        phone: Optional = None,
        email: Optional[str] = None,
        card_track: Optional[str] = None,
        card_number: Optional[str] = None,
        name: Optional[str] = None,
        middle_name: Optional[str] = None,
        sur_name: Optional[str] = None,
        birthday: Optional[str] = None,
        sex: Optional[str] = None,
        consent_status: Optional[str] = None,
        should_receive_promo_actions_info: Optional[bool] = None,
        referrer_id: Optional[str] = None,
        user_data: Optional[str] = None,
        id: str = None,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
    ):
        data = {
            "organizationId": organization_id,
        }

        if id is not None:
            data["id"] = id
        if phone is not None:
            data["phone"] = phone
        if card_track is not None:
            data["cardTrack"] = card_track
        if card_number is not None:
            data["cardNumber"] = card_number
        if name is not None:
            data["name"] = name
        if middle_name is not None:
            data["middleName"] = middle_name
        if sur_name is not None:
            data["surName"] = sur_name
        if birthday is not None:
            data["birthday"] = birthday
        if email is not None:
            data["email"] = email
        if sex is not None:
            data["sex"] = sex
        if consent_status is not None:
            data["consentStatus"] = consent_status
        if should_receive_promo_actions_info is not None:
            data["shouldReceivePromoActionsInfo"] = should_receive_promo_actions_info
        if referrer_id is not None:
            data["referrerId"] = referrer_id
        if user_data is not None:
            data["userData"] = user_data

        try:
            return self._post_request(
                url="/api/1/loyalty/iiko/customer/create_or_update",
                data=data,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(
                f"Не удалось создать или обновить клиента: \n{err}"
            )
        except TypeError as err:
            raise TypeError(f"Не удалось: \n{err}")

    def refill_customer_balance(
        self,
        organization_id: str,
        customer_id: str = None,
        wallet_id: Optional[str] = None,
        sum: float = None,
        comment: Optional[str] = None,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
    ):
        """
        Начислить пользователю средств на баланс
        :param organization_id: id организации
        :param customer_id: id пользователя
        :param wallet_id: id кошелька
        :param sum: Сумма (только положительное число)
        :param comment: Комментарий к платежу
        :return:
        """

        data = {
            "organizationId": organization_id,
        }

        if customer_id is not None:
            data["customerId"] = (customer_id,)
        if wallet_id is not None:
            data["walletId"] = wallet_id
        if sum is not None:
            data["sum"] = abs(sum)
        if comment is not None:
            data["comment"] = comment

        try:
            return self._post_request(
                url="/api/1/loyalty/iiko/customer/wallet/topup/",
                data=data,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(
                f"Не удалось создать или обновить клиента: \n{err}"
            )
        except TypeError as err:
            raise TypeError(f"Не удалось: \n{err}")


class Order(BaseAPI):
    def retrieve_order_by_tables(self):
        pass


class Deliveries(BaseAPI):
    def retrieve_orders_by_date_and_status(
        self,
        organization_id: List[str],
        delivery_date_from: Union[datetime, str],
        delivery_date_to: Union[datetime, str] = None,
        statuses: list = None,
        source_keys: list = None,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
    ) -> Response:
        """
        Возвращает список заказов по дате и статусу
        :param organization_id: id организации
        :param delivery_date_from: дата начала заказов в формате yyyy-MM-dd HH:mm:ss.fff
        :param delivery_date_to: дата окончания заказов в формате yyyy-MM-dd HH:mm:ss.fff
        :param statuses: список статусов заказов. Список: "Unconfirmed", "WaitCooking", "ReadyForCooking", "CookingStarted", "CookingCompleted", "Waiting", "OnWay", "Delivered", "Closed", "Cancelled"
        :param source_keys: список источников заказов
        :param timeout: время ожидания запроса
        :return:
        """

        # https://api-ru.iiko.services/api/1/deliveries/by_delivery_date_and_status

        data = {
            "organizationIds": organization_id,
        }

        if isinstance(delivery_date_from, datetime):
            data["deliveryDateFrom"] = delivery_date_from.strftime(self.strfdt)
        elif isinstance(delivery_date_from, str):
            data["deliveryDateFrom"] = delivery_date_from

        if isinstance(delivery_date_to, datetime):
            data["deliveryDateTo"] = delivery_date_to.strftime(self.strfdt)
        elif isinstance(delivery_date_to, str):
            data["deliveryDateTo"] = delivery_date_to
        if delivery_date_to is not None:
            if isinstance(delivery_date_to, datetime):
                data["deliveryDateTo"] = delivery_date_to.strftime(self.strfdt)
            elif isinstance(delivery_date_to, str):
                data["deliveryDateTo"] = delivery_date_to
            else:
                raise TypeError("type delivery_date_to != datetime or str")

        if statuses is not None:
            if not isinstance(statuses, list):
                raise TypeError("type statuses!= list")
            data["statuses"] = statuses

        if source_keys is not None:
            if not isinstance(source_keys, list):
                raise TypeError("type source_keys!= list")
            data["sourceKeys"] = source_keys

        try:
            return self._post_request(
                url="/api/1/deliveries/by_delivery_date_and_status",
                data=data,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(
                f"Не удалось получить список заказов по дате и статусу: \n{err}"
            )
        except TypeError as err:
            raise TypeError(
                f"Ошибка в методе retrieve_orders_by_date_and_status: \n{err}"
            )


class Dictionaries(BaseAPI):
    def discounts(
        self,
        organization_ids: List[str],
        timeout=BaseAPI.DEFAULT_TIMEOUT,
    ) -> Response:
        if not bool(organization_ids):
            raise TypeError("Пустой список организаций")

        data = {
            "organizationIds": organization_ids,
        }

        try:
            return self._post_request(
                url="/api/1/discounts",
                data=data,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(
                f"Не удалось получить скидки/надбавки: \n{err}"
            )
        except TypeError as err:
            raise TypeError(f"Ошибка в методе discounts: \n{err}")


class IikoCloudAPI(Customers, Order, Deliveries, Dictionaries):
    pass
