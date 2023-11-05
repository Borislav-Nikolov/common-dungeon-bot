from firebase_admin import db


global server_reference_ids_ref


def init_channels_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global server_reference_ids_ref
    server_reference_ids_ref = db.reference(f"{prefix}/server_reference_ids")


def set_player_message_id(player_id, message_id):
    server_reference_ids_ref.child("player_message_ids").update(
        {
            f'{player_id}': f'{message_id}'
        }
    )


def get_player_message_id(player_id) -> str:
    return server_reference_ids_ref.get()['player_message_ids'][f'{player_id}']


def get_shop_message_id() -> int:
    return get_server_reference_id("message_id")


def get_shop_channel_id() -> int:
    return get_server_reference_id("shop_channel_id")


def get_characters_info_channel_id() -> int:
    return get_server_reference_id("character_info_channel_id")


def get_static_shop_channel_id() -> int:
    return get_server_reference_id("static_shop_channel_id")


def get_server_reference_id(variable_name) -> int:
    return server_reference_ids_ref.get()[variable_name]


def set_shop_message_id(message_id):
    set_server_reference_id("message_id", message_id)


def set_shop_channel_id(shop_channel_id):
    set_server_reference_id("shop_channel_id", shop_channel_id)


def set_character_info_channel_id(character_info_channel_id):
    set_server_reference_id("character_info_channel_id", character_info_channel_id)


def set_static_shop_channel_id(static_shop_channel_id):
    set_server_reference_id("static_shop_channel_id", static_shop_channel_id)


def set_server_reference_id(variable_name, reference_id):
    data = server_reference_ids_ref.get()
    if data is None:
        data = dict()
    data[variable_name] = reference_id
    server_reference_ids_ref.set(data)
