from typing import Optional
from api import consolerequests


def set_inventory_console_message_id(message_id, channel_id):
    return consolerequests.set_inventory_console_message_id(message_id, channel_id)


def get_inventory_console_message_id() -> Optional[str]:
    return consolerequests.get_inventory_console_message_id()


def get_inventory_console_channel_id() -> Optional[str]:
    return consolerequests.get_inventory_console_channel_id()


def set_reserved_items_console_message_id(message_id, channel_id):
    return consolerequests.set_reserved_items_console_message_id(message_id, channel_id)


def get_reserved_items_console_message_id() -> Optional[str]:
    return consolerequests.get_reserved_items_console_message_id()


def get_reserved_items_console_channel_id() -> Optional[str]:
    return consolerequests.get_reserved_items_console_channel_id()


def set_shop_generate_console_message_id(message_id, channel_id):
    return consolerequests.set_shop_generate_console_message_id(message_id, channel_id)


def get_shop_generate_console_message_id() -> Optional[str]:
    return consolerequests.get_shop_generate_console_message_id()


def get_shop_generate_console_channel_id() -> Optional[str]:
    return consolerequests.get_shop_generate_console_channel_id()


def set_character_status_console_message_id(message_id, channel_id):
    return consolerequests.set_character_status_console_message_id(message_id, channel_id)


def get_character_status_console_message_id() -> Optional[str]:
    return consolerequests.get_character_status_console_message_id()


def get_character_status_console_channel_id() -> Optional[str]:
    return consolerequests.get_character_status_console_channel_id()
