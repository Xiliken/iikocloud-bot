from ctypes import Union
from typing import List, Any

from pyiikocloudapi import IikoTransport
from pyiikocloudapi.models import CouriersModel

from bot.mics.helpers.Config import Config

__api = IikoTransport(Config.get('IIKOCLOUD_LOGIN'))


def get_organizations_ids() -> list[str]:
    """
    Получить id организаций
    :return:
    """
    organizations = __api.organizations(return_additional_info=True).organizations

    return [item.id for item in organizations]
