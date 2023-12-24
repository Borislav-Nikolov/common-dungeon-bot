from util import botutils
from provider import channelsprovider


async def handle_server_initialization_prompts(message) -> bool:
    init_key = '$init.'
    full_message = str(message.content)
    if full_message.startswith(init_key) and botutils.is_admin_message(message):
        init_key_length = len(init_key)
        init_message = full_message[init_key_length:]
        if init_message == 'shop':
            await handle_shop_init(message)
        elif init_message == 'characters':
            await handle_characters_init(message)
        return True
    return False


async def handle_shop_init(message):
    channelsprovider.initialize_shop_channel(message.channel.id)
    await message.channel.send('Channel initialized as the Shop channel.')


async def handle_characters_init(message):
    channelsprovider.initialize_characters_channel(message.channel.id)
    await message.channel.send('Channel initialized as the Characters Info channel.')
