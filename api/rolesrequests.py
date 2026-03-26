import requests

import api.base
from api.base import api_url
from typing import Optional


def set_role_id(role_name, role_id) -> bool:
    url = api_url('set_role_id')
    data = {'role_name': role_name, 'role_id': role_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def get_role_id(role_name) -> Optional[str]:
    url = api_url('get_role_id')
    params = {'role_name': role_name}
    response = requests.get(url, params=params, headers=api.base.get_bearer_token_headers())
    if response.status_code == 404:
        return None
    return str(response.json()['role_id'])


def delete_role_id(role_name) -> bool:
    url = api_url('delete_role_id')
    data = {'role_name': role_name}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def set_moderator_role_id(role_id) -> bool:
    return set_role_id('moderator', role_id)


def get_moderator_role_id() -> Optional[str]:
    return get_role_id('moderator')


def delete_moderator_role_id() -> bool:
    return delete_role_id('moderator')
