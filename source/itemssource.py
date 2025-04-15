from api import itemrequests


def get_all_items() -> list:
    return itemrequests.get_all_items()


def get_all_minor_items() -> list:
    return itemrequests.get_all_minor_items()


def get_all_major_items() -> list:
    return itemrequests.get_all_major_items()
