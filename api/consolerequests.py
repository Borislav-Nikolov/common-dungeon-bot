import requests
from api.base import api_url, get_bearer_token_headers
from typing import Optional


def set_inventory_console_message_id(message_id, channel_id) -> bool:
    url = api_url('set_inventory_console_message_id')
    data = {
        'message_id': message_id,
        'channel_id': channel_id
    }
    response = requests.post(url, json=data, headers=get_bearer_token_headers())
    return response.ok


def get_inventory_console_message_id() -> Optional[str]:
    url = api_url('get_inventory_console_message_id')
    response = requests.get(url, headers=get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json().get('message_id')


def get_inventory_console_channel_id() -> Optional[str]:
    url = api_url('get_inventory_console_channel_id')
    response = requests.get(url, headers=get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json().get('channel_id')


def set_reserved_items_console_message_id(message_id, channel_id) -> bool:
    url = api_url('set_reserved_items_console_message_id')
    data = {
        'message_id': message_id,
        'channel_id': channel_id
    }
    response = requests.post(url, json=data, headers=get_bearer_token_headers())
    return response.ok


def get_reserved_items_console_message_id() -> Optional[str]:
    url = api_url('get_reserved_items_console_message_id')
    response = requests.get(url, headers=get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json().get('message_id')


def get_reserved_items_console_channel_id() -> Optional[str]:
    url = api_url('get_reserved_items_console_channel_id')
    response = requests.get(url, headers=get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json().get('channel_id')


def set_shop_generate_console_message_id(message_id, channel_id) -> bool:
    url = api_url('set_shop_generate_console_message_id')
    data = {
        'message_id': message_id,
        'channel_id': channel_id
    }
    response = requests.post(url, json=data, headers=get_bearer_token_headers())
    return response.ok


def get_shop_generate_console_message_id() -> Optional[str]:
    url = api_url('get_shop_generate_console_message_id')
    response = requests.get(url, headers=get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json().get('message_id')


def get_shop_generate_console_channel_id() -> Optional[str]:
    url = api_url('get_shop_generate_console_channel_id')
    response = requests.get(url, headers=get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json().get('channel_id')


def set_character_status_console_message_id(message_id, channel_id) -> bool:
    url = api_url('set_character_status_console_message_id')
    data = {
        'message_id': message_id,
        'channel_id': channel_id
    }
    response = requests.post(url, json=data, headers=get_bearer_token_headers())
    return response.ok


def get_character_status_console_message_id() -> Optional[str]:
    url = api_url('get_character_status_console_message_id')
    response = requests.get(url, headers=get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json().get('message_id')


def get_character_status_console_channel_id() -> Optional[str]:
    url = api_url('get_character_status_console_channel_id')
    response = requests.get(url, headers=get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json().get('channel_id')
