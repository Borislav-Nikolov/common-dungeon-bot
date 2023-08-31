from provider import channelsprovider


def is_admin(message) -> bool:
    try:
        return message.author.guild_permissions.administrator
    except AttributeError:
        return False


def is_characters_info_channel(message) -> bool:
    return message.channel.id == channelsprovider.get_characters_info_channel_id()


def is_shop_channel(message) -> bool:
    return message.channel.id == channelsprovider.get_shop_channel_id()
