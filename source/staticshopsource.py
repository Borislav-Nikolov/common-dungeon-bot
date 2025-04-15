from api import staticshoprequests


def update_in_static_shop(data: dict):
    staticshoprequests.update_in_static_shop(data)


def get_static_shop_item(item_id: str) -> dict:
    return staticshoprequests.get_static_shop_item(item_id)
