import asyncio

import discord
import utils
import firebase
import magicshop
import characters


def run_discord_bot(bot_token):
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            content = str(message.content)
            if is_characters_info_channel(message) and content.startswith('<@'):
                firebase.set_player_message_id(utils.strip_id_tag(content), message.id)
            return

        username = str(message.author.id)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        if user_message.startswith('$'):
            await handle_server_initialization_prompts(message)
            await handle_shop_commands(message, client)
            await handle_character_commands(message, client)

    @client.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == client.user.id:
            return
        channel = client.get_channel(payload.channel_id)
        if channel.id == firebase.get_shop_channel_id() and payload.message_id == firebase.get_shop_message_id():
            shop_message = await channel.fetch_message(payload.message_id)
            accept_emoji = '\U00002705'
            decline_emoji = '\U0000274C'
            item_index = utils.emoji_to_index(str(payload.emoji))
            item_name = magicshop.get_item_name_by_index(item_index)
            if item_name is None:
                await channel.send(f"<@{payload.user_id}>, sorry but that item was already sold.")
                await shop_message.remove_reaction(payload.emoji, payload.member)
                raise Exception("Item not found in shop.")

            def check_accept(reaction, user):
                return user.id == payload.user_id and (str(reaction.emoji) == accept_emoji or str(reaction.emoji) == decline_emoji)

            bot_message = await channel.send(f'<@{payload.user_id}>, are you sure you want to buy {item_name}?')
            await bot_message.add_reaction(accept_emoji)
            await bot_message.add_reaction(decline_emoji)
            try:
                reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check_accept)
                if str(reaction.emoji) == accept_emoji:
                    sold_item_name = magicshop.sell_item(payload.user_id, item_index)
                    sold = len(sold_item_name) != 0
                    if sold:
                        shop_string = magicshop.get_current_shop_string()
                        await shop_message.edit(content=shop_string)
                        await refresh_player_message(client, payload.user_id)
                        await channel.send(magicshop.get_sold_item_string(payload.user_id, sold_item_name))
                        if magicshop.get_item_name_by_index(item_index) is not None:
                            await shop_message.remove_reaction(payload.emoji, payload.member)
                    else:
                        await channel.send(magicshop.get_failed_to_buy_item_string(payload.user_id, item_name))
                        await shop_message.remove_reaction(payload.emoji, payload.member)
                else:
                    await channel.send(f'Order of {item_name} was declined.')
                    await shop_message.remove_reaction(payload.emoji, payload.member)
            except asyncio.TimeoutError:
                await channel.send(f'Order of {item_name} has timed out.')
                await shop_message.remove_reaction(payload.emoji, payload.member)

    client.run(bot_token)


async def handle_server_initialization_prompts(message):
    init_key = '$init.'
    full_message = str(message.content)
    if full_message.startswith(init_key) and is_admin(message):
        init_key_length = len(init_key)
        init_message = full_message[init_key_length:]
        if init_message == 'shop':
            firebase.set_shop_channel_id(message.channel.id)
            await message.channel.send('Channel initialized as the Shop channel.')
        elif init_message == 'characters':
            firebase.set_character_info_channel_id(message.channel.id)
            await message.channel.send('Channel initialized as the Characters Info channel.')


async def handle_shop_commands(message, client):
    shop_key = '$shop'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == shop_key and is_shop_channel(message):
        command_message = keywords[1]
        if command_message == 'generate' and is_admin(message):
            character_levels_csv = keywords[2]
            new_shop_message = await message.channel.send(magicshop.generate_new_magic_shop(character_levels_csv))
            firebase.set_shop_message_id(new_shop_message.id)
            for index in range(1, magicshop.SHOP_MAX_NUMBER_OF_ITEMS + 1):
                await new_shop_message.add_reaction(utils.index_to_emoji(index))
        elif command_message == 'refresh' and is_admin(message):
            shop_message = await message.channel.fetch_message(firebase.get_shop_message_id())
            await shop_message.edit(content=magicshop.get_current_shop_string())
        elif command_message == 'repost' and is_admin(message):
            new_shop_message = await message.channel.send(magicshop.get_current_shop_string())
            firebase.set_shop_message_id(new_shop_message.id)
            for index in range(1, magicshop.SHOP_MAX_NUMBER_OF_ITEMS + 1):
                await new_shop_message.add_reaction(utils.index_to_emoji(index))
        elif command_message.isnumeric():
            shop_message = await message.channel.fetch_message(firebase.get_shop_message_id())
            sold_item_name = magicshop.sell_item(message.author.id, int(command_message))
            sold = len(sold_item_name) != 0
            if sold:
                shop_string = magicshop.get_current_shop_string()
                await shop_message.edit(content=shop_string)
                await refresh_player_message(client, message.author.id)
                await message.add_reaction('🪙')
                await message.channel.send(magicshop.get_sold_item_string(message.author.id, sold_item_name))
            else:
                await message.add_reaction('❌')
        elif command_message == 'sell' and not keywords[2].isnumeric() and is_admin(message):
            # expected: player_tag,rarity,rarity level
            sell_data = utils.split_strip(keywords[2], ',')
            player_id = utils.strip_id_tag(sell_data[0])
            sold = magicshop.refund_item(player_id, sell_data[1], sell_data[2])
            if sold:
                await refresh_player_message(client, player_id)
                await message.add_reaction('🪙')
            else:
                await message.add_reaction('❌')
        elif command_message == 'sell' and keywords[2].isnumeric():
            player_id = message.author.id
            item_name = magicshop.refund_item_by_index(player_id, int(keywords[2]))
            sold = len(item_name) > 0
            if sold:
                await refresh_player_message(client, player_id)
                await message.add_reaction('🪙')
                await message.channel.send(magicshop.get_refunded_item_string(player_id, item_name))
            else:
                await message.add_reaction('❌')
        elif command_message == 'help':
            item_index = keywords[2]
            if not item_index.isnumeric():
                raise Exception("Invalid index format.")
            item_description = magicshop.get_shop_item_description(item_index)
            await message.author.send(item_description)


async def refresh_player_message(client, player_id):
    await update_player_message(client, player_id, characters.get_up_to_date_player_message(player_id))


async def update_player_message(client, player_id, new_message):
    players_channel = client.get_channel(firebase.get_character_info_channel_id())
    player_message_id = firebase.get_player_message_id(player_id)
    player_message = await players_channel.fetch_message(player_message_id)
    await player_message.edit(content=new_message)


async def handle_character_commands(message, client):
    characters_key = '$characters'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == characters_key and is_admin(message):
        if keywords[1] == "hardinit":
            player_id = utils.strip_id_tag(keywords[2])
            characters.hardinit_player(player_id, keywords[3])
            players_channel = client.get_channel(firebase.get_character_info_channel_id())
            await players_channel.send(characters.get_up_to_date_player_message(player_id))
        elif is_characters_info_channel(message):
            if keywords[1] == "addsession":
                if characters.add_session(keywords[2]):
                    split_data = utils.split_strip(keywords[2], ',')
                    player_ids = list(
                        map(lambda it: utils.strip_id_tag(it if it.find('-') == -1 else it[0:it.find('-')]), split_data))
                    for player_id in player_ids:
                        await refresh_player_message(client, player_id)
                    await message.add_reaction('🪙')
                else:
                    await message.add_reaction('❌')
            elif keywords[1] == "addplayer":
                player_data_list = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_data_list[0])
                player_data_list.pop(0)
                characters.add_player(player_id, player_data_list)
                players_channel = client.get_channel(firebase.get_character_info_channel_id())
                await players_channel.send(characters.get_up_to_date_player_message(player_id))
            elif keywords[1] == "addcharacter":
                data_list = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(data_list[0])
                data_list.pop(0)
                characters.add_character(player_id, data_list)
                await refresh_player_message(client, player_id)
            elif keywords[1] == "deletecharacter":
                player_id_to_character_name = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_id_to_character_name[0])
                characters.delete_character(player_id, player_id_to_character_name[1])
                await refresh_player_message(client, player_id)
            elif keywords[1] == "changename":
                player_id_and_names = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_id_and_names[0])
                characters.change_character_name(player_id, player_id_and_names[1], player_id_and_names[2])
                await refresh_player_message(client, player_id)
            elif keywords[1] == "swapclasslevels":
                player_id_and_params = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_id_and_params[0])
                characters.swap_class_levels(
                    player_id, player_id_and_params[1], player_id_and_params[2], player_id_and_params[3])
                await refresh_player_message(client, player_id)
            elif keywords[1] == "repost":
                player_id = utils.strip_id_tag(keywords[2])
                await message.channel.send(characters.get_up_to_date_player_message(player_id))
    # non-admin commands
    elif keywords[0] == characters_key:
        if keywords[1] == "inventory":
            inventory_string = characters.get_inventory_string(message.author.id)
            await message.author.send(inventory_string)


def is_admin(message) -> bool:
    try:
        return message.author.guild_permissions.administrator
    except AttributeError:
        return False


def is_characters_info_channel(message) -> bool:
    return message.channel.id == firebase.get_character_info_channel_id()


def is_shop_channel(message) -> bool:
    return message.channel.id == firebase.get_shop_channel_id()
