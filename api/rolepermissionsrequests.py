import requests
from api.base import api_url, get_bearer_token_headers
from typing import Optional


def get_permitted_roles(action_name: str) -> Optional[list]:
    url = api_url('get_permitted_roles')
    params = {'action_name': action_name}
    response = requests.get(url, params=params, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return None


def update_permitted_roles(action_name: str, roles: list[str]) -> bool:
    url = api_url('update_permitted_roles')
    data = {'action_name': action_name, 'roles': roles}
    response = requests.post(url, json=data, headers=get_bearer_token_headers())
    return response.ok
