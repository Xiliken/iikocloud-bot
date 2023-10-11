import xml.etree.ElementTree as ET

from bot.mics import Config
from services.iikoserver.IikoServer import IikoServer


def get_departments():
    iiko_server = IikoServer(
        login=Config.get("IIKOSERVER_LOGIN"),
        password=Config.get("IIKOSERVER_PASSWORD"),
        domain=Config.get("IIKOSERVER_DOMAIN"),
    )

    departments = iiko_server.departments()

    tree = ET.fromstring(departments)
    results = []

    # Получить все элементы corporateItemDto
    corporate_item_dtos = tree.findall("corporateItemDto")

    # Итерировать по элементам corporateItemDto
    for corporate_item_dto in corporate_item_dtos:
        # Получить id
        id = corporate_item_dto.find("id").text

        # Получить name
        name = corporate_item_dto.find("name").text

        # Получить type
        type = corporate_item_dto.find("type").text

        # Добавить элемент в список результатов, если его тип равен DEPARTMENT
        if type == "DEPARTMENT":
            results.append({"id": id, "name": name})

    return results
