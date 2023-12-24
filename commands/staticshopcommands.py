from util import utils, botutils, itemutils
from provider import channelsprovider, itemsprovider, staticshopprovider
from controller import staticshop


async def handle_static_shop_commands(message) -> bool:
    static_shop_key = '$staticshop'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == static_shop_key and botutils.is_admin_message(message):
        if keywords[1] == 'init':
            await handle_static_shop_initialization(message)
        return True
    return False


async def handle_static_shop_initialization(message):
    channelsprovider.initialize_static_shop_channel(message.channel.id)
    all_minor_items = itemsprovider.get_all_minor_items()
    for item in all_minor_items:
        new_message = await message.channel.send(itemutils.get_static_shop_message(item))
        await new_message.add_reaction('🪙')
        staticshopprovider.add_or_update_in_static_shop(data={new_message.id: staticshop.item_to_shop_item(item)})
