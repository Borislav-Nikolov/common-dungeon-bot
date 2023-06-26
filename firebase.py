import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# TODO: split into different "source" files for items, shop, characters, servers/channels

global shop_ref
global server_reference_ids_ref
global players_ref


def init_firebase(project: str, is_test: bool):
    cred_obj = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred_obj, {'databaseURL': project})
    prefix = "/test" if is_test else ""
    global shop_ref
    global server_reference_ids_ref
    global players_ref
    shop_ref = db.reference(f"{prefix}/magic_shop_items")
    server_reference_ids_ref = db.reference(f"{prefix}/server_reference_ids")
    players_ref = db.reference(f"{prefix}/players")


def get_magic_shop_items() -> list:
    return shop_ref.get()


def get_player(player_id) -> dict:
    return players_ref.get()[f'{player_id}']


def get_players(player_ids: list) -> dict:
    player_list = dict()
    all_players = players_ref.get()
    index = 0
    for player in all_players:
        player_id = list(all_players.keys())[index]
        if player_id in player_ids:
            player_list[player] = all_players[player]
        index += 1
    return player_list


def set_in_magic_shop(items: list):
    shop_ref.set(items)


def set_shop_message_id(message_id):
    set_server_reference_id("message_id", message_id)


def set_player_message_id(player_id, message_id):
    server_reference_ids_ref.child("player_message_ids").update(
        {
            f'{player_id}': f'{message_id}'
        }
    )


def get_player_message_id(player_id) -> str:
    return server_reference_ids_ref.get()['player_message_ids'][f'{player_id}']


def set_shop_channel_id(shop_channel_id):
    set_server_reference_id("shop_channel_id", shop_channel_id)


def set_character_info_channel_id(character_info_channel_id):
    set_server_reference_id("character_info_channel_id", character_info_channel_id)


def set_server_reference_id(variable_name, reference_id):
    data = server_reference_ids_ref.get()
    if data is None:
        data = dict()
    data[variable_name] = reference_id
    server_reference_ids_ref.set(data)


def update_in_players(player_data):
    players_ref.update(player_data)


def get_shop_message_id() -> int:
    return get_server_reference_id("message_id")


def get_shop_channel_id() -> int:
    return get_server_reference_id("shop_channel_id")


def get_characters_info_channel_id() -> int:
    return get_server_reference_id("character_info_channel_id")


def get_server_reference_id(variable_name) -> int:
    return server_reference_ids_ref.get()[variable_name]
