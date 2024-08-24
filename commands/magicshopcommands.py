from util import utils, botutils
from controller import characters, magicshop
from provider import channelsprovider
from bridge import charactersbridge


async def handle_shop_commands(message, client) -> bool:
    shop_key = '$shop'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    # SHOP CHANNEL COMMANDS
    if keywords[0] == shop_key and botutils.is_shop_channel(message):
        command_message = keywords[1]
        # ADMIN COMMANDS
        if command_message == 'generate' and botutils.is_admin_message(message):
            await handle_generate(message.channel, character_levels_csv=keywords[2])
        elif command_message == 'refresh' and botutils.is_admin_message(message):
            await handle_refresh(message)
        elif command_message == 'repost' and botutils.is_admin_message(message):
            await handle_repost(message)
        elif command_message == 'sell' and not keywords[2].isnumeric() and botutils.is_admin_message(message):
            await handle_sell_item_by_rarity(client, message, tag_rarity_raritylevel_csv=keywords[2])
        # NON-ADMIN COMMANDS
        elif command_message == 'sell' and keywords[2].isnumeric():
            await handle_sell_item_by_inventory_ordinal(client, message, item_ordinal=int(keywords[2]))
        elif command_message.isnumeric():
            await handle_buy_item(client, message, command_message)
        elif command_message == 'help':
            await handle_item_help_request(message, item_index=keywords[2])
        return True
    return False


async def handle_generate(shop_channel, character_levels_csv):
    new_shop_message = await shop_channel.send(magicshop.generate_new_magic_shop(character_levels_csv))
    channelsprovider.set_shop_message_id(new_shop_message.id)
    for index in range(1, magicshop.SHOP_MAX_NUMBER_OF_ITEMS + 1):
        await new_shop_message.add_reaction(utils.index_to_emoji(index))


async def handle_refresh(message):
    shop_message = await message.channel.fetch_message(channelsprovider.get_shop_message_id())
    await shop_message.edit(content=magicshop.get_current_shop_string())


async def handle_repost(message):
    new_shop_message = await message.channel.send(magicshop.get_current_shop_string())
    channelsprovider.set_shop_message_id(new_shop_message.id)
    for index in range(1, magicshop.SHOP_MAX_NUMBER_OF_ITEMS + 1):
        await new_shop_message.add_reaction(utils.index_to_emoji(index))


async def handle_buy_item(client, message, command_message):
    shop_message = await message.channel.fetch_message(channelsprovider.get_shop_message_id())
    sold_item_name = magicshop.sell_item(message.author.id, int(command_message))
    sold = len(sold_item_name) != 0
    if sold:
        shop_string = magicshop.get_current_shop_string()
        await shop_message.edit(content=shop_string)
        await charactersbridge.refresh_player_message(client, message.author.id)
        await message.add_reaction('🪙')
        await message.channel.send(magicshop.get_sold_item_string(message.author.id, sold_item_name))
    else:
        await message.add_reaction('❌')


async def handle_sell_item_by_rarity(client, message, tag_rarity_raritylevel_csv):
    # expected: player_tag,rarity,rarity level
    sell_data = utils.split_strip(tag_rarity_raritylevel_csv, ',')
    player_id = utils.strip_id_tag(sell_data[0])
    sold = magicshop.refund_item(player_id, sell_data[1], sell_data[2])
    if sold:
        await charactersbridge.refresh_player_message(client, player_id)
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_sell_item_by_inventory_ordinal(client, message, item_ordinal):
    player_id = message.author.id
    item_name = characters.refund_item_by_index(player_id, item_ordinal)
    sold = len(item_name) > 0
    if sold:
        await charactersbridge.refresh_player_message(client, player_id)
        await message.add_reaction('🪙')
        await message.channel.send(magicshop.get_refunded_item_string(player_id, item_name))
    else:
        await message.add_reaction('❌')


async def handle_item_help_request(message, item_index):
    if not item_index.isnumeric():
        raise Exception("Invalid index format.")
    item_description = magicshop.get_shop_item_description(item_index)
    for description_part in item_description:
        await message.author.send(description_part)
