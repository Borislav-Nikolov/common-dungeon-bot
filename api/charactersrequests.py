import requests

import api.base
from api.base import api_url
from model.addsessiondata import AddSessionData
from model.addplayerdata import AddPlayerData
from model.addcharacterdata import AddCharacterData
from model.playerstatus import PlayerStatus
from model.playerrole import PlayerRole


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


def make_delete_character_request(player_id, character_name: str) -> bool:
    url = api_url('delete_character')
    data = {
        'player_id': player_id,
        'character_name': character_name
    }
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def make_change_character_name_request(player_id, old_character_name: str, new_character_name: str) -> bool:
    url = api_url('change_character_name')
    data = {
        'player_id': player_id,
        'old_character_name': old_character_name,
        'new_character_name': new_character_name
    }
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def make_swap_character_class_levels_request(
        player_id,
        character_name: str,
        class_to_remove_from: str,
        class_to_add_to: str
) -> bool:
    url = api_url('swap_character_class_levels')
    data = {
        'player_id': player_id,
        'character_name': character_name,
        'class_to_remove_from': class_to_remove_from,
        'class_to_add_to': class_to_add_to
    }
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def make_change_player_status_request(
        player_id,
        new_player_status: PlayerStatus
) -> bool:
    url = api_url('change_player_status')
    data = {
        'player_id': player_id,
        'player_status': new_player_status.name
    }
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def make_change_player_role_request(
        player_id,
        new_player_role: PlayerRole
) -> bool:
    url = api_url('change_player_role')
    data = {
        'player_id': player_id,
        'player_role': new_player_role.name
    }
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.status_code == 200


def get_player(player_id, include_inventory=True, include_characters=True):
    url = api_url('get_player')
    params = {
        "include_inventory": str(include_inventory).lower(),
        "include_characters": str(include_characters).lower(),
        'player_id': str(player_id)
    }
    response = requests.get(url, params=params, headers=api.base.get_bearer_token_headers())
    if not response.ok:
        return None
    return response.json()


def get_all_players(include_inventory=True, include_characters=True) -> dict:
    url = api_url('get_all_players')
    params = {
        "include_inventory": str(include_inventory).lower(),
        "include_characters": str(include_characters).lower()
    }
    response = requests.get(url, params=params, headers=api.base.get_bearer_token_headers())
    if not response.ok:
        return {}
    return response.json()


def update_in_players(players_data: dict) -> bool:
    url = api_url('update_in_players')
    data = {"players_data": players_data}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.ok


def delete_player(player_id) -> bool:
    url = api_url('delete_player')
    data = {'player_id': player_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.ok


def make_set_character_max_level_request(player_id, character_name, max_level) -> bool:
    url = api_url('set_character_max_level')
    data = {
        'player_id': player_id,
        'character_name': character_name,
        'max_level': max_level
    }
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.ok


def make_add_missing_bundles_request(player_id) -> bool:
    url = api_url('add_missing_bundles')
    data = {'player_id': player_id}
    response = requests.post(url, json=data, headers=api.base.get_bearer_token_headers())
    return response.ok
