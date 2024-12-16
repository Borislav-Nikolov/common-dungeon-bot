import requests

import api.base
from api.base import api_url
from model.addsessiondata import AddSessionData
from model.addplayerdata import AddPlayerData
from model.addcharacterdata import AddCharacterData


def make_add_session_request(data: dict[str, AddSessionData]) -> bool:
    url = api_url('add_player_session')
    data_list = list()
    for session_data_key in data:
        session_data = data[session_data_key]
        data_list.append({
            'player_id': session_data.player_id,
            'character_name': session_data.character_name,
            'class_name': session_data.class_name,
            'is_dm': session_data.is_dm
        })
    response = requests.post(url, json=data_list, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def make_remove_session_request(data: dict[str, AddSessionData]) -> bool:
    url = api_url('remove_player_session')
    data_list = list()
    for session_data_key in data:
        session_data = data[session_data_key]
        data_list.append({
            'player_id': session_data.player_id,
            'character_name': session_data.character_name,
            'class_name': session_data.class_name,
            'is_dm': session_data.is_dm
        })
    response = requests.post(url, json=data_list, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def make_add_player_request(add_player_data: AddPlayerData) -> bool:
    url = api_url('add_player')
    data = {
        'player_id': add_player_data.player_id,
        'player_name': add_player_data.player_name,
        'character_name': add_player_data.character_name,
        'class_name': add_player_data.class_name
    }
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def make_add_character_request(add_character_data: AddCharacterData) -> bool:
    url = api_url('add_character')
    data = {
        'player_id': add_character_data.player_id,
        'character_name': add_character_data.character_name,
        'character_level': add_character_data.character_level,
        'classes_data': list(
            map(
                lambda class_data: {
                    'class_name': class_data.class_name,
                    'class_level': class_data.class_level
                },
                add_character_data.classes_data
            )
        )
    }
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200
