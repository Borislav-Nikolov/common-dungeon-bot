from source import consolesource
from typing import Optional


def set_inventory_console_message_id(message_id, channel_id):
    consolesource.set_inventory_console_message_id(message_id, channel_id)


def get_inventory_console_message_id() -> Optional[str]:
    return consolesource.get_inventory_console_message_id()


def get_inventory_console_channel_id() -> Optional[str]:
    return consolesource.get_inventory_console_channel_id()


def set_shop_generate_console_message_id(message_id, channel_id):
    consolesource.set_shop_generate_console_message_id(message_id, channel_id)


def get_shop_generate_console_message_id() -> Optional[str]:
    return consolesource.get_shop_generate_console_message_id()


def get_shop_generate_console_channel_id() -> Optional[str]:
    return consolesource.get_shop_generate_console_channel_id()
