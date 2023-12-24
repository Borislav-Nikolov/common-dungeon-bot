import discord.errors

from util import utils, botutils
from controller import posts


async def handle_posts_commands(message) -> bool:
    posts_key = '$posts'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == posts_key and botutils.is_admin_message(message):
        if keywords[1] == 'post':
            await handle_post_message(message)
        return True
    return False


async def handle_post_message(message):
    post_message = utils.remove_first_line(message.content)
    post_message_length = len(post_message)
    if post_message_length == 0:
        await message.channel.send('Enter a text after the command. Max 1850 characters.')
    elif post_message_length > 1850:
        await message.channel.send('Text is too long. It must not be more than 1850 characters.')
    else:
        new_post = await message.channel.send(post_message)
        posts.add_post(posts_channel_id=message.channel.id, post_message_id=new_post.id)
        await new_post.add_reaction(posts.arrow_up_emoji)
        await new_post.add_reaction(posts.arrow_down_emoji)
        await new_post.add_reaction(posts.edit_emoji)
        try:
            await message.delete()
        except discord.errors.NotFound:
            print("Post creating prompt message was deleted.")
