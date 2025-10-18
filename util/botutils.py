import discord

from api import channelsrequests
from typing import Callable, Awaitable, Optional
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
    return message.channel.id == channelsrequests.get_characters_info_channel_id()


def is_shop_channel(message) -> bool:
    return message.channel.id == channelsrequests.get_shop_channel_id()


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


async def search_forum_titles(
        bot,
        forum_channel_id: int,
        search_terms: list[str],
        case_sensitive: bool = False,
        prefer_exact_match: bool = True
) -> dict[str, Optional[str]]:
    results: dict[str, Optional[str]] = {term: None for term in search_terms}
    partial_matches: dict[str, Optional[str]] = {term: None for term in search_terms}

    forum = await bot.fetch_channel(forum_channel_id)
    if not forum or not isinstance(forum, discord.ForumChannel):
        raise ValueError()

    # Collect all threads
    all_threads = list(forum.threads)
    try:
        async for thread in forum.archived_threads(limit=None):
            all_threads.append(thread)
    except discord.Forbidden:
        pass

    for thread in all_threads:
        thread_title = thread.name if case_sensitive else thread.name.lower()

        for term in search_terms:
            search_term = term if case_sensitive else term.lower()
            discord_link = f"https://discord.com/channels/{forum.guild.id}/{thread.id}"

            # Check for exact match first (if preferred)
            if prefer_exact_match and thread_title == search_term:
                results[term] = discord_link
            # Check for partial match
            elif search_term in thread_title:
                if prefer_exact_match:
                    # Store as partial match, only use if no exact match found
                    if partial_matches[term] is None:
                        partial_matches[term] = discord_link
                else:
                    # Use first partial match found
                    if results[term] is None:
                        results[term] = discord_link

    # Fill in partial matches for terms that didn't get exact matches
    if prefer_exact_match:
        for term in search_terms:
            if results[term] is None and partial_matches[term] is not None:
                results[term] = partial_matches[term]

    return results
