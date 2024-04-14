import discord

from provider import channelsprovider
from typing import Callable, Awaitable
from discord import Message
import asyncio


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


async def create_emoji_prompt(
        client,
        user_id,
        emoji_list: list[str],
        on_emoji_click: Callable[[str], Awaitable[bool]],
        on_timeout: Callable[[], Awaitable[Message]],
        prompt_message: Callable[[], Awaitable],
        timeout=30.0,
        timeout_after_interaction=300.0
):
    bot_message = await prompt_message()

    for added_emoji in emoji_list:
        await bot_message.add_reaction(added_emoji)

    def check_command_emoji(inner_payload):
        inner_user_id = inner_payload.user_id
        inner_emoji = str(inner_payload.emoji)
        return inner_user_id == user_id and bot_message.id == inner_payload.message_id and any(
            emoji == inner_emoji for emoji in emoji_list)

    try:
        prompt_done = False
        current_timeout = timeout
        while not prompt_done:
            result_payload = await client.wait_for('raw_reaction_add', timeout=current_timeout,
                                                   check=check_command_emoji)
            clicked_emoji = str(result_payload.emoji)
            emoji_index = emoji_list.index(clicked_emoji)
            prompt_done = await on_emoji_click(emoji_list[emoji_index])
            current_timeout = timeout_after_interaction
    except asyncio.TimeoutError:
        await on_timeout()


def is_dm_channel(channel) -> bool:
    return isinstance(channel, discord.DMChannel)


def get_role_id_tag(role_id) -> str:
    return f'<@&{role_id}>'


def strip_role_id_tag(role_id_tag: str) -> str:
    return role_id_tag.strip()[3:role_id_tag.find('>')]
