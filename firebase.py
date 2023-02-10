import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json


global items_ref
global shop_ref
global server_reference_ids_ref


def get_all_items_from_firebase():
    return items_ref.get()


def get_magic_shop_items():
    return shop_ref.get()


def init_firebase_items_refs(is_test: bool):
    cred_obj = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred_obj, {
        'databaseURL': 'https://commondungeonbot-default-rtdb.europe-west1.firebasedatabase.app/'
    })
    global items_ref
    global shop_ref
    global server_reference_ids_ref
    prefix = "/test" if is_test else ""
    items_ref = db.reference("/all_items")
    shop_ref = db.reference(f"{prefix}/magic_shop_items")
    server_reference_ids_ref = db.reference(f"{prefix}/server_reference_ids")


def init_in_firebase(json_path):
    with open(json_path, 'r') as items:
        file_contents = json.load(items)
    items_ref.set(file_contents)


def set_in_magic_shop(items):
    shop_ref.set(items)


def set_shop_message_id(message_id):
    set_server_reference_id("message_id", message_id)


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


def get_shop_message_id() -> int:
    return get_server_reference_id("message_id")


def get_shop_channel_id() -> int:
    return get_server_reference_id("shop_channel_id")


def get_character_info_channel_id() -> int:
    return get_server_reference_id("character_info_channel_id")


def get_server_reference_id(variable_name) -> int:
    return server_reference_ids_ref.get()[variable_name]

