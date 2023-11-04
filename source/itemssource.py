from firebase_admin import db
from source.sourcefields import *
import json


global items_ref


def init_items_source(is_test: bool):
    # TODO: fix test item list in database
    prefix = "/test" if is_test else ""
    global items_ref
    items_ref = db.reference(f"all_items")


def get_all_items() -> list:
    return items_ref.get()


def update_in_items(item_data):
    items_ref.update(item_data)


def get_all_minor_items():
    return sorted(
        items_ref.order_by_child(ITEM_FIELD_RARITY_LEVEL).equal_to("MINOR").get().values(),
        key=lambda value: value[ITEM_FIELD_NAME]
    )


def get_all_major_items():
    return sorted(
        items_ref.order_by_child(ITEM_FIELD_RARITY_LEVEL).equal_to("MAJOR").get().values(),
        key=lambda value: value[ITEM_FIELD_NAME]
    )


# Used to initialize the items in the database.
def init_in_firebase(json_path):
    with open(json_path, 'r', encoding='utf-8') as items:
        file_contents = json.load(items)
    items_ref.set(file_contents)
