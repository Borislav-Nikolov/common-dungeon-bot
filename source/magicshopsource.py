from api import magicshoprequests


def get_magic_shop_items() -> list:
    return magicshoprequests.get_magic_shop_items()


def set_in_magic_shop(items: list):
    return magicshoprequests.set_in_magic_shop(items)
