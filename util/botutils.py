from provider import channelsprovider


def is_admin_message(message) -> bool:
    return is_admin(user=message.author)


def is_admin(user) -> bool:
    try:
        return user.guild_permissions.administrator
    except AttributeError:
        return False


def is_characters_info_channel(message) -> bool:
    return message.channel.id == channelsprovider.get_characters_info_channel_id()


def is_shop_channel(message) -> bool:
    return message.channel.id == channelsprovider.get_shop_channel_id()
