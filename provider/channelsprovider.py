from source import channelssource


def initialize_shop_channel(channel_id):
    channelssource.set_shop_channel_id(channel_id)


def initialize_characters_channel(channel_id):
    channelssource.set_character_info_channel_id(channel_id)


def initialize_static_shop_channel(channel_id):
    channelssource.set_static_shop_channel_id(channel_id)


def get_characters_info_channel_id() -> int:
    return channelssource.get_characters_info_channel_id()


def get_shop_channel_id() -> int:
    return channelssource.get_shop_channel_id()


def get_static_shop_channel_id() -> int:
    return channelssource.get_static_shop_channel_id()


def set_player_message_id(player_id, message_id):
    channelssource.set_player_message_id(player_id, message_id)


def set_shop_message_id(message_id):
    channelssource.set_shop_message_id(message_id)


def get_shop_message_id() -> int:
    return channelssource.get_shop_message_id()


def get_player_message_id(player_id) -> str:
    return channelssource.get_player_message_id(player_id)
