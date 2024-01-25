from firebase_admin import db
from typing import Optional

global console_ref

CONSOLE_KEY_INVENTORY = 'inventory'
CONSOLE_KEY_SHOP_GENERATE = 'shop_generate'
CONSOLE_KEY_MESSAGE_ID = 'message_id'
CONSOLE_KEY_CHANNEL_ID = 'channel_id'


def init_console_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global console_ref
    console_ref = db.reference(f"{prefix}/console")


def set_inventory_console_message_id(message_id, channel_id):
    console_ref.child(CONSOLE_KEY_INVENTORY).update(
        {
            CONSOLE_KEY_MESSAGE_ID: f'{message_id}',
            CONSOLE_KEY_CHANNEL_ID: f'{channel_id}'
        }
    )


def get_inventory_console_message_id() -> Optional[str]:
    data = console_ref.get()
    return data[CONSOLE_KEY_INVENTORY][
        CONSOLE_KEY_MESSAGE_ID] if data is not None and CONSOLE_KEY_INVENTORY in data else None


def get_inventory_console_channel_id() -> Optional[str]:
    data = console_ref.get()
    return data[CONSOLE_KEY_INVENTORY][
        CONSOLE_KEY_CHANNEL_ID] if data is not None and CONSOLE_KEY_INVENTORY in data else None


def set_shop_generate_console_message_id(message_id, channel_id):
    console_ref.child(CONSOLE_KEY_SHOP_GENERATE).update(
        {
            CONSOLE_KEY_MESSAGE_ID: f'{message_id}',
            CONSOLE_KEY_CHANNEL_ID: f'{channel_id}'
        }
    )


def get_shop_generate_console_message_id() -> Optional[str]:
    data = console_ref.get()
    return data[CONSOLE_KEY_SHOP_GENERATE][
        CONSOLE_KEY_MESSAGE_ID] if data is not None and CONSOLE_KEY_SHOP_GENERATE in data else None


def get_shop_generate_console_channel_id() -> Optional[str]:
    data = console_ref.get()
    return data[CONSOLE_KEY_SHOP_GENERATE][
        CONSOLE_KEY_CHANNEL_ID] if data is not None and CONSOLE_KEY_SHOP_GENERATE in data else None
