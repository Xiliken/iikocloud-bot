from pyiikocloudapi import IikoTransport
from pyiikocloudapi.models import CouriersModel

from bot.mics.helpers.Config import Config

__api = IikoTransport(Config.get("IIKOCLOUD_LOGIN"))


def get_organizations_ids() -> list[str]:
    """
    Получить id организаций
    :return:
    """
    organizations = __api.organizations(return_additional_info=True).organizations

    return [item.id for item in organizations]


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
