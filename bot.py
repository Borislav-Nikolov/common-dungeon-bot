
import discord

import reactionhandler
import utils
import firebase
import magicshop
import characters
import itemutils


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
            await handle_homebrew_commands(message, client)

    @client.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == client.user.id:
            return
        channel = client.get_channel(payload.channel_id)
        if channel.id == firebase.get_shop_channel_id() and payload.message_id == firebase.get_shop_message_id():
            await reactionhandler.handle_magic_shop_reaction(payload, channel, client)

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
                await characters.refresh_player_message(client, message.author.id)
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
                await characters.refresh_player_message(client, player_id)
                await message.add_reaction('🪙')
            else:
                await message.add_reaction('❌')
        elif command_message == 'sell' and keywords[2].isnumeric():
            player_id = message.author.id
            item_name = magicshop.refund_item_by_index(player_id, int(keywords[2]))
            sold = len(item_name) > 0
            if sold:
                await characters.refresh_player_message(client, player_id)
                await message.add_reaction('🪙')
                await message.channel.send(magicshop.get_refunded_item_string(player_id, item_name))
            else:
                await message.add_reaction('❌')
        elif command_message == 'help':
            item_index = keywords[2]
            if not item_index.isnumeric():
                raise Exception("Invalid index format.")
            item_description = magicshop.get_shop_item_description(item_index)
            for description_part in item_description:
                await message.author.send(description_part)


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
                        await characters.refresh_player_message(client, player_id)
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
                await characters.refresh_player_message(client, player_id)
            elif keywords[1] == "deletecharacter":
                player_id_to_character_name = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_id_to_character_name[0])
                characters.delete_character(player_id, player_id_to_character_name[1])
                await characters.refresh_player_message(client, player_id)
            elif keywords[1] == "changename":
                player_id_and_names = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_id_and_names[0])
                characters.change_character_name(player_id, player_id_and_names[1], player_id_and_names[2])
                await characters.refresh_player_message(client, player_id)
            elif keywords[1] == "swapclasslevels":
                player_id_and_params = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_id_and_params[0])
                characters.swap_class_levels(
                    player_id, player_id_and_params[1], player_id_and_params[2], player_id_and_params[3])
                await characters.refresh_player_message(client, player_id)
            elif keywords[1] == "repost":
                player_id = utils.strip_id_tag(keywords[2])
                await message.channel.send(characters.get_up_to_date_player_message(player_id))
    # non-admin commands
    elif keywords[0] == characters_key:
        if keywords[1] == "inventory":
            inventory_string = characters.get_inventory_string(message.author.id)
            await message.author.send(inventory_string)


async def handle_homebrew_commands(message, client):
    homebrew_key = '$homebrew'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == homebrew_key and is_admin(message):
        if keywords[1] == 'item':
            new_item = dict()
            new_item[itemutils.ITEM_FIELD_OFFICIAL] = False

            def check_author(checked_message):
                return checked_message.author.id == message.author.id

            # TODO: apply function to the rest of the prompts
            # Input item name
            await item_creation_prompt(
                client=client,
                message=message,
                bot_message="Input item **name**.\n```yaml\nMax 48 symbols.\n```",
                error_message="Item name is too long. Try again.",
                timeout=60.0,
                new_item=new_item,
                new_item_parameter=itemutils.ITEM_FIELD_NAME,
                check_input=lambda name: len(name) <= 48,
                produce_result=lambda name: name
            )

            can_continue = False

            # Input item description
            def check_item_description(description):
                return len(description) <= 2048
            while not can_continue:
                await message.author.send("Input item **description**.\n```yaml\nMax 1024 symbols.\n```")
                item_creator_reply = await client.wait_for('message', timeout=300.0, check=check_author)
                can_continue = check_item_description(item_creator_reply.content)
                if not can_continue:
                    await message.author.send("Description is too long. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_DESCRIPTION] = item_creator_reply.content
            can_continue = False

            # Input item rarity
            def check_item_rarity_input(rarity):
                try:
                    utils.rarity_to_ordinal(rarity)
                except ValueError:
                    return False
                return True
            while not can_continue:
                await message.author.send(
                    "Input item **rarity**.\n```yaml\n"
                    "Possible values: common, uncommon, rare, very rare, legendary\n```")
                item_creator_reply = await client.wait_for('message', timeout=120.0, check=check_author)
                can_continue = check_item_rarity_input(item_creator_reply.content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_RARITY] = item_creator_reply.content.capitalize()
            can_continue = False

            # Input item rarity level
            def check_item_rarity_level_input(rarity_level):
                lowered_rarity_level = rarity_level.lower()
                return lowered_rarity_level == "minor" or lowered_rarity_level == "major"
            while not can_continue:
                await message.author.send("Input item **rarity level**.\n```yaml\nPossible values: minor, major\n```")
                item_creator_reply = await client.wait_for('message', timeout=120.0, check=check_author)
                can_continue = check_item_rarity_level_input(item_creator_reply.content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_RARITY_LEVEL] = item_creator_reply.content.upper()
            can_continue = False

            # It item consumable
            def check_item_consumable(consumable):
                lowered_consumable = consumable.lower()
                return lowered_consumable == "yes" or lowered_consumable == "no"
            while not can_continue:
                await message.author.send("Is item **consumable**?\n```yaml\nPossible values: Yes, No\n```")
                item_creator_reply = await client.wait_for('message', timeout=60.0, check=check_author)
                lowered_content = item_creator_reply.content.lower()
                can_continue = check_item_consumable(lowered_content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_CONSUMABLE] = True if lowered_content == "yes" else False
            can_continue = False

            # Is item attunable
            def check_item_attunable(attunable):
                lowered_attunable = attunable.lower()
                return lowered_attunable == "yes" or lowered_attunable == "no"
            while not can_continue:
                await message.author.send("Is item **attunable**?\n```yaml\nPossible values: Yes, No\n```")
                item_creator_reply = await client.wait_for('message', timeout=60.0, check=check_author)
                lowered_content = item_creator_reply.content.lower()
                can_continue = check_item_attunable(lowered_content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_ATTUNEMENT] = True if lowered_content == "yes" else False
            can_continue = False

            # Is item banned from the Magic Shop
            def check_item_banned(banned):
                lowered_banned = banned.lower()
                return lowered_banned == "yes" or lowered_banned == "no"
            while not can_continue:
                await message.author.send(
                    "Is item **banned** from the Magic Shop?\n```yaml\nPossible values: Yes, No\n```")
                item_creator_reply = await client.wait_for('message', timeout=60.0, check=check_author)
                lowered_content = item_creator_reply.content.lower()
                can_continue = check_item_banned(lowered_content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_BANNED] = True if lowered_content == "yes" else False
            can_continue = False

            # Confirm item creation
            confirmed = False

            def check_confirmation(confirmation):
                lowered_confirmation = confirmation.lower()
                return lowered_confirmation == "yes" or lowered_confirmation == "no"
            while not can_continue:
                await message.author.send(
                    "Confirm creation of item:\n" +
                    itemutils.get_homebrew_item_confirmation_description(new_item) +
                    "```yaml\nPossible values: Yes, No\n```")
                item_creator_reply = await client.wait_for('message', timeout=300.0, check=check_author)
                lowered_content = item_creator_reply.content.lower()
                can_continue = check_confirmation(lowered_content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    confirmed = True if lowered_content == "yes" else False

            if confirmed:
                firebase.update_in_items(new_item)
                await message.author.send(f'**{new_item[itemutils.ITEM_FIELD_NAME]}** was created.')
            else:
                await message.author.send(f'**{new_item[itemutils.ITEM_FIELD_NAME]}** was NOT created.')


def is_admin(message) -> bool:
    try:
        return message.author.guild_permissions.administrator
    except AttributeError:
        return False


def is_characters_info_channel(message) -> bool:
    return message.channel.id == firebase.get_character_info_channel_id()


def is_shop_channel(message) -> bool:
    return message.channel.id == firebase.get_shop_channel_id()


async def item_creation_prompt(
        client,
        message,
        bot_message: str,
        error_message: str,
        timeout,
        new_item: dict,
        new_item_parameter: str,
        check_input,
        produce_result
):

    can_continue = False

    def check_author(checked_message):
        return checked_message.author.id == message.author.id

    try:
        while not can_continue:
            await message.author.send(bot_message)
            item_creator_reply = await client.wait_for('message', timeout=timeout, check=check_author)
            lowered_content = item_creator_reply.content.lower()
            can_continue = check_input(lowered_content)
            if not can_continue:
                await message.author.send(error_message)
            else:
                new_item[new_item_parameter] = produce_result(lowered_content)
    except asyncio.TimeoutError:
        await message.author.send("Item creation timed out.")
        raise Exception()
