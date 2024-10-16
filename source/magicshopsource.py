import requests
from api.base import api_url


def get_magic_shop_items() -> list:
    return requests.get(api_url('magic_shop_items')).json()


def set_in_magic_shop(items: list):
    response = requests.post(api_url('set_magic_shop_items'), json=items)
    if response.status_code == 200:
        print("Set magic shop request was successful.")
    else:
        print(f"Set magic shop request failed with status code: {response.status_code}.")
