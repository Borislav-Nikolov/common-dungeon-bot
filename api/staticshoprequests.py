import requests
from api.base import api_url, get_bearer_token_headers


def get_static_shop_item(item_id: str) -> dict:
    url = api_url('get_static_shop_item')
    params = {'item_id': item_id}
    response = requests.get(url, params=params, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return {}


def update_in_static_shop(static_shop_data) -> bool:
    url = api_url('update_in_static_shop')
    data = {'static_shop_data': static_shop_data}
    response = requests.post(url, json=data, headers=get_bearer_token_headers())
    return response.ok
