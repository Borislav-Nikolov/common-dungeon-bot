import requests

import api.base
from api.base import api_url


def initialize_shop_channel(channel_id) -> bool:
    url = api_url('initialize_shop_channel')
    data = {'channel_id': channel_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def initialize_characters_channel(channel_id) -> bool:
    url = api_url('initialize_characters_channel')
    data = {'channel_id': channel_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def initialize_static_shop_channel(channel_id) -> bool:
    url = api_url('initialize_static_shop_channel')
    data = {'channel_id': channel_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def get_characters_info_channel_id() -> int:
    url = api_url('get_characters_info_channel_id')
    response = requests.get(url, headers=api.base.get_bearer_token_headers())
    return response.json()['channel_id']


def get_shop_channel_id() -> int:
    url = api_url('get_shop_channel_id')
    response = requests.get(url, headers=api.base.get_bearer_token_headers())
    return response.json()['channel_id']


def get_static_shop_channel_id() -> int:
    url = api_url('get_static_shop_channel_id')
    response = requests.get(url, headers=api.base.get_bearer_token_headers())
    return response.json()['channel_id']


def set_player_message_id(player_id, message_id) -> bool:
    url = api_url('set_player_message_id')
    data = {'player_id': player_id, 'message_id': message_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def set_shop_message_id(message_id) -> bool:
    url = api_url('set_shop_message_id')
    data = {'message_id': message_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def get_shop_message_id() -> int:
    url = api_url('get_shop_message_id')
    response = requests.get(url, headers=api.base.get_bearer_token_headers())
    return response.json()['message_id']


def get_player_message_id(player_id) -> int:
    url = api_url('get_player_message_id')
    data = {'player_id': player_id}
    response = requests.get(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.json()['message_id']


def delete_player_message_id(player_id) -> bool:
    url = api_url('delete_player_message_id')
    data = {'player_id': player_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200
