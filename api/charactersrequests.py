import requests

import api.base
from api.base import api_url
from model.addsessiondata import AddSessionData


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
