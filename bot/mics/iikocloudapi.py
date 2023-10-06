import datetime
from typing import Union

from bot.mics import normalize_phone_number
from bot.mics.helpers.Config import Config
from services.iikocloud.iIkoCloud import IikoCloudAPI

__api = IikoCloudAPI(Config.get("IIKOCLOUD_LOGIN"))


def get_organizations_ids() -> list[str]:
    """
    Получить id организаций
    :return:
    """
    organizations = __api.organizations(return_additional_info=True)["organizations"]

    return [item["id"] for item in organizations]


def check_iiko_user_exists(data) -> bool:
    if "errorDescription" in data:
        error_description = data["errorDescription"]
        if "There is no user with phone" in error_description:
            # Пользователя не существует
            return False
        else:
            return False
    elif "id" in data:
        # Если есть поле id, то пользователь явно существует
        return True


def get_last_order(user_phone: Union[str, int] = None):
    """
    Получить последний заказ
    :return:
    """
    if user_phone is None:
        raise Exception("Phone number not specified")
    elif len(user_phone) < 10:  # Потому что если придет номер 9222222222, то он сам подставит 7
        raise Exception("Invalid phone number format")

    orders_by_organizations = __api.retrieve_orders_by_phone_number(
        phone=f"+{normalize_phone_number(user_phone)}",
        organizations_ids=[Config.get("IIKOCLOUD_ORGANIZATIONS_IDS", "list")[0]],
    )

    last_order = None
    for organization in orders_by_organizations["ordersByOrganizations"]:
        for order in organization["orders"]:
            last_order = order["order"]
            break
    return last_order


def check_last_closed_order(user_phone: Union[str, int] = None) -> bool:
    """
    Проверить дату последнего закрытого заказа
    :param user_phone: Номер телефона пользователя (номер карты Iiko)
    :return: Если статус закрыт и дата последнего заказа равна текущей даты, то возвращаем True, иначе False
    """
    last_order = get_last_order(user_phone=user_phone)

    if last_order is None:
        return None

    order_closed_date = datetime.datetime.strptime(last_order["whenClosed"], "%Y-%m-%d %H:%M:%S.%f")

    # Получаем дату последнего закрытого заказа у пользователя из БД

    if last_order["status"] == "CLOSED" and order_closed_date.date() == datetime.datetime.now().date():
        return True
    else:
        return False
