from firebase_admin import db
from source.sourcefields import *
from typing import Optional
import copy


global players_ref
global players_path
global player_inventories_ref
global player_inventories_path
global player_characters_ref
global player_characters_path


def init_players_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global players_path
    players_path = f"{prefix}/players"
    global players_ref
    players_ref = db.reference(players_path)
    global player_inventories_path
    player_inventories_path = f"{prefix}/player_inventories"
    global player_inventories_ref
    player_inventories_ref = db.reference(player_inventories_path)
    global player_characters_path
    player_characters_path = f"{prefix}/player_characters"
    global player_characters_ref
    player_characters_ref = db.reference(player_characters_path)


def get_player(player_id, include_inventory=True, include_characters=True) -> Optional[dict]:
    string_id = str(player_id)
    player_data = players_ref.order_by_key().equal_to(string_id).get()
    if player_data:
        player_object = player_data[string_id]
        return assemble_player(player_id, player_object, include_inventory, include_characters)
    return None


def get_players(player_ids: list, include_inventory=True, include_characters=True) -> dict:
    players = dict()
    for player_id in player_ids:
        players[player_id] = get_player(
            player_id=player_id,
            include_inventory=include_inventory,
            include_characters=include_characters
        )
    return players


def assemble_player(player_id, player_object, include_inventory, include_characters):
    string_id = str(player_id)
    # Migrate inventory and characters to other references. Remove redundant code when all players are migrated.
    migrate_player_data = False
    player_object_copy = copy.deepcopy(player_object)
    if PLAYER_FIELD_INVENTORY in player_object:
        migrate_player_data = True
        inventory = player_object[PLAYER_FIELD_INVENTORY]
        update_in_player_inventories({string_id: inventory})
        player_object_copy.pop(PLAYER_FIELD_INVENTORY)
    elif include_inventory:
        inventory_data = get_player_inventory(string_id)
        if inventory_data:
            player_object[PLAYER_FIELD_INVENTORY] = inventory_data
    if PLAYER_FIELD_CHARACTERS in player_object:
        migrate_player_data = True
        characters = player_object[PLAYER_FIELD_CHARACTERS]
        update_in_player_characters({string_id: characters})
        player_object_copy.pop(PLAYER_FIELD_CHARACTERS)
    elif include_characters:
        characters_data = get_player_characters(string_id)
        if characters_data:
            player_object[PLAYER_FIELD_CHARACTERS] = characters_data
    if migrate_player_data:
        update_in_players({string_id: player_object_copy})
    if not include_inventory and PLAYER_FIELD_INVENTORY in player_object:
        player_object.pop(PLAYER_FIELD_INVENTORY)
    if not include_characters and PLAYER_FIELD_CHARACTERS in player_object:
        player_object.pop(PLAYER_FIELD_CHARACTERS)
    return player_object


def get_players_by_status(player_status: str, include_inventory=True, include_characters=True) -> dict:
    players = dict()
    players_data = players_ref.order_by_child(PLAYER_FIELD_PLAYER_STATUS).equal_to(player_status).get()
    for player_id in players_data:
        player_object = players_data[player_id]
        players[player_id] = assemble_player(
            player_id=player_id,
            player_object=player_object,
            include_inventory=include_inventory,
            include_characters=include_characters
        )
    return players


def get_all_players(include_inventory=True, include_characters=True) -> dict:
    players = dict()
    players_data = players_ref.get()
    for player_id in players_data:
        player_object = players_data[player_id]
        players[player_id] = assemble_player(
            player_id=player_id,
            player_object=player_object,
            include_inventory=include_inventory,
            include_characters=include_characters
        )
    return players


def get_player_inventory(player_id):
    string_id = str(player_id)
    inventory_data = player_inventories_ref.order_by_key().equal_to(string_id).get()
    if inventory_data:
        return inventory_data[player_id]
    else:
        return None


def get_player_characters(player_id):
    string_id = str(player_id)
    characters_data = player_characters_ref.order_by_key().equal_to(string_id).get()
    if characters_data:
        return characters_data[player_id]
    else:
        return None


def update_in_players(players_data):
    for player_id in players_data:
        player_object = players_data[player_id]
        if PLAYER_FIELD_INVENTORY in player_object:
            update_in_player_inventories({player_id: player_object[PLAYER_FIELD_INVENTORY]})
            player_object.pop(PLAYER_FIELD_INVENTORY)
        if PLAYER_FIELD_CHARACTERS in player_object:
            update_in_player_characters({player_id: player_object[PLAYER_FIELD_CHARACTERS]})
            player_object.pop(PLAYER_FIELD_CHARACTERS)
        players_data[player_id] = player_object
        players_ref.update(players_data)


def update_in_player_inventories(inventory_data):
    player_inventories_ref.update(inventory_data)


def update_in_player_characters(characters_data):
    player_characters_ref.update(characters_data)


def delete_player(player_id):
    player_ref = db.reference(f'{players_path}/{player_id}')
    player_ref.delete()
    player_inventory_ref = db.reference(f'{player_inventories_path}/{player_id}')
    player_inventory_ref.delete()
    player_characters_list_ref = db.reference(f'{player_characters_path}/{player_id}')
    player_characters_list_ref.delete()
