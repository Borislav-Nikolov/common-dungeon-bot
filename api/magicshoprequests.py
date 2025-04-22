import requests
from api.base import api_url, get_bearer_token_headers


def get_magic_shop_items() -> list:
    url = api_url('get_magic_shop_items')
    response = requests.get(url, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return []


def set_in_magic_shop(items: list) -> bool:
    url = api_url('set_in_magic_shop')
    data = {'items': items}
    response = requests.post(url, json=data, headers=get_bearer_token_headers())
    return response.ok


def get_magic_shop_last_date() -> int:
    url = api_url('get_magic_shop_last_date')
    response = requests.get(url, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()['magic_shop_last_date']
    return -1
