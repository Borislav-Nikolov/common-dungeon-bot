import asyncio

import discord.errors

from provider import postsprovider
from util import utils
from controller import posts
from model.post import Post
from typing import Optional
from discord import NotFound
from util import botutils


async def handle_posts_reactions(payload, channel, client, post_message):
    if post_message.author == client.user:
        post_section = postsprovider.get_post_section_group(channel.id, post_message.id)
        post_message_index = utils.find_index(post_section.posts, lambda post: post.post_id == str(post_message.id))
        if post_message_index != -1:
            role_ids = list(map(lambda it: it.id, payload.member.roles))
            post_group_name = post_section.posts[post_message_index].post_group_name
            if botutils.is_admin(payload.member) or posts.any_has_permissions(post_group_name, role_ids):
                payload_emoji = str(payload.emoji)
                if payload_emoji == posts.arrow_up_emoji:
                    await handle_arrow_up_emoji(channel, post_message, payload)
                elif payload_emoji == posts.arrow_down_emoji:
                    await handle_arrow_down_emoji(channel, post_message, payload)
                elif payload_emoji == posts.edit_emoji:
                    await handle_edit_emoji(channel, post_message, payload, client)


async def handle_arrow_up_emoji(channel, post_message, payload):
    await handle_arrow_emoji(
        channel=channel,
        post_message=post_message,
        retrieve_adjacent_post=lambda channel_id, post_message_id: posts.get_post_before(channel_id, post_message_id)
    )
    await post_message.remove_reaction(payload.emoji, payload.member)


async def handle_arrow_down_emoji(channel, post_message, payload):
    await handle_arrow_emoji(
        channel=channel,
        post_message=post_message,
        retrieve_adjacent_post=lambda channel_id, post_message_id: posts.get_post_after(channel_id, post_message_id)
    )
    await post_message.remove_reaction(payload.emoji, payload.member)


async def handle_arrow_emoji(channel, post_message, retrieve_adjacent_post):
    while True:
        adjacent_post: Optional[Post] = retrieve_adjacent_post(channel.id, post_message.id)
        if adjacent_post is None:
            break
        try:
            adjacent_post_message = await channel.fetch_message(adjacent_post.post_id)
            post_message_content = post_message.content
            adjacent_post_message_content = adjacent_post_message.content
            await post_message.edit(content=adjacent_post_message_content)
            await adjacent_post_message.edit(content=post_message_content)
            break
        except NotFound:
            posts.remove_post(channel.id, adjacent_post.post_id)
            continue


async def handle_edit_emoji(channel, post_message, payload, client):
    prompt_message = await channel.send(f'<@{payload.member.id}>, post your edited version of {post_message.jump_url}.')
    await prompt_message.edit(suppress=True)

    def check_author(checked_message):
        return checked_message.author.id == payload.member.id and checked_message.channel.id == channel.id

    try:
        edited_message = await client.wait_for('message', timeout=120.0, check=check_author)
        await post_message.edit(content=edited_message.content)
        try:
            await edited_message.delete()
        except discord.errors.NotFound:
            print("Edited post message not found. May be caused by editing two posts simultaneously.")
        await prompt_message.delete()
        await post_message.remove_reaction(payload.emoji, payload.member)
    except asyncio.TimeoutError:
        await prompt_message.delete()
