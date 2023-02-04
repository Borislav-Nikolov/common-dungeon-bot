import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json


global items_ref
global shop_ref
global shop_message_ref


def get_all_items_from_firebase():
    return items_ref.get()


def get_magic_shop_items():
    return shop_ref.get()


def init_firebase_items_refs():
    cred_obj = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred_obj, {
        'databaseURL': 'https://commondungeonbot-default-rtdb.europe-west1.firebasedatabase.app/'
    })
    global items_ref
    global shop_ref
    global shop_message_ref
    items_ref = db.reference("/all_items")
    shop_ref = db.reference("/magic_shop_items")
    shop_message_ref = db.reference("/magic_shop_message_id")


def init_in_firebase(json_path):
    with open(json_path, 'r') as items:
        file_contents = json.load(items)
    items_ref.set(file_contents)


def set_in_magic_shop(items):
    shop_ref.set(items)


def set_shop_message_id(message_id):
    data = {"message_id": message_id}
    shop_message_ref.set(data)

