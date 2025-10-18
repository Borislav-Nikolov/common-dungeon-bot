from util import botutils, utils
from api import channelsrequests


async def handle_server_initialization_prompts(message) -> bool:
    init_key = '$init'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == init_key and botutils.is_admin_message(message):
        if keywords[1] == 'shop':
            await handle_shop_init(message)
        elif keywords[1] == 'characters':
            await handle_characters_init(message)
        elif keywords[1] == 'charactersforum':
            await handle_characters_forum_init(message, keywords[2])
        return True
    return False


async def handle_shop_init(message):
    channelsrequests.initialize_shop_channel(message.channel.id)
    await message.channel.send('Channel initialized as the Shop channel.')


async def handle_characters_init(message):
    channelsrequests.initialize_characters_channel(message.channel.id)
    await message.channel.send('Channel initialized as the Characters Info channel.')


async def handle_characters_forum_init(message, forum_channel_id):
    if channelsrequests.initialize_characters_forum_channel(forum_channel_id):
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')
