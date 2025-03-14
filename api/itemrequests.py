import requests
from api.base import api_url, get_bearer_token_headers


def get_all_items() -> list:
    url = api_url('get_all_items')
    response = requests.get(url, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return []


def get_all_minor_items() -> list:
    url = api_url('get_all_minor_items')
    response = requests.get(url, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return []


def get_all_major_items() -> list:
    url = api_url('get_all_major_items')
    response = requests.get(url, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return []
