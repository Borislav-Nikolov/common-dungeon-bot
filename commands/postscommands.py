import discord.errors

from util import utils, botutils
from controller import posts


async def handle_posts_commands(message) -> bool:
    posts_key = '$posts'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == posts_key:
        post_group_name = keywords[1]
        if posts.is_group_allowed(post_group_name):
            if len(keywords) > 2 and botutils.is_admin_message(message):
                command_name = keywords[2]
                role_id = botutils.strip_role_id_tag(keywords[3])
                if command_name == 'permissionadd':
                    await handle_add_permissions(message, post_group_name, role_id)
                elif command_name == 'permissionremove':
                    await handle_remove_permissions(message, post_group_name, role_id)
                else:
                    await message.channel.send("Wrong command.")
            elif botutils.is_admin_message(message) or posts.any_has_permissions(
                    post_group_name=post_group_name,
                    role_ids=list(map(lambda discord_role: discord_role.id, message.author.roles))):
                await handle_post_message(
                    message=message,
                    post_group_name=post_group_name,
                    post_creator_id=message.author.id
                )
            elif len(keywords) == 2:
                await message.channel.send(
                    f"You don't have permissions to add posts for posting group '{post_group_name}'.")
        else:
            await message.channel.send("Wrong post group name.")
        return True
    return False


async def handle_add_permissions(message, post_group_name: str, role_id: str):
    if posts.add_permitted_role(post_group_name, role_id):
        await message.channel.send(
            f"Added posting permissions to {botutils.get_role_id_tag(role_id)} for '{post_group_name}'.")
    else:
        await message.channel.send("Could not add permission.")


async def handle_remove_permissions(message, post_group_name: str, role_id: str):
    if posts.remove_permitted_role(post_group_name, role_id):
        await message.channel.send(
            f"Removed posting permissions from {botutils.get_role_id_tag(role_id)} for '{post_group_name}'.")
    else:
        await message.channel.send("Could not remove permission.")


async def handle_post_message(message, post_group_name, post_creator_id):
    post_message = utils.remove_first_line(message.content)
    post_message_length = len(post_message)
    if post_message_length == 0:
        await message.channel.send('Enter a text after the command. Max 1850 characters.')
    elif post_message_length > 1850:
        await message.channel.send('Text is too long. It must not be more than 1850 characters.')
    else:
        new_post = await message.channel.send(post_message)
        posts.add_post(
            posts_channel_id=message.channel.id,
            post_message_id=new_post.id,
            post_group_name=post_group_name,
            post_creator_id=post_creator_id
        )
        await new_post.add_reaction(posts.arrow_up_emoji)
        await new_post.add_reaction(posts.arrow_down_emoji)
        await new_post.add_reaction(posts.edit_emoji)
        try:
            await message.delete()
        except discord.errors.NotFound:
            print("Post creating prompt message was deleted.")
