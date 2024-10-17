import requests


def get_magic_shop_items() -> list:
    return requests.get('http://localhost:8081/magic_shop_items').json()


def set_in_magic_shop(items: list):
    response = requests.post('http://localhost:8081/set_magic_shop_items', json=items)
    if response.status_code == 200:
        print("Set magic shop request was successful.")
    else:
        print(f"Set magic shop request failed with status code: {response.status_code}.")
