import requests

import api.base
from api.base import api_url


def get_characters_info_channel_id() -> int:
    url = api_url('get_characters_info_channel_id')
    response = requests.get(url, headers=api.base.get_bearer_token_headers())
    return response.json()['channel_id']


def set_player_message_id(player_id, message_id) -> bool:
    url = api_url('set_player_message_id')
    data = {'player_id': player_id, 'message_id': message_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200
