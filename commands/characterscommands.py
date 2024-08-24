from controller import characters
from provider import channelsprovider
from util import utils, botutils
from model.addsessiondata import AddSessionData
from bridge import charactersbridge


async def handle_character_commands(message, client) -> bool:
    characters_key = '$characters'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == characters_key:
        # ADMIN COMMANDS
        if botutils.is_admin_message(message):
            # CHARACTERS INFO CHANNEL
            if botutils.is_characters_info_channel(message):
                if keywords[1] == "addsession":
                    await handle_addsession(client, message, session_data_csv=keywords[2])
                elif keywords[1] == "removesession":
                    await handle_removesession(client, message, session_data_csv=keywords[2])
                elif keywords[1] == "refreshmessage":
                    await handle_refresh_player_message(client, player_ids_csv=keywords[2])
                elif keywords[1] == "addplayer":
                    await handle_addplayer(client, player_data_csv=keywords[2])
                elif keywords[1] == "addcharacter":
                    await handle_addcharacter(client, data_csv=keywords[2])
                elif keywords[1] == "deletecharacter":
                    await handle_deletecharacter(client, player_id_char_name_csv=keywords[2])
                elif keywords[1] == "changename":
                    await handle_changename(client, player_id_names_csv=keywords[2])
                elif keywords[1] == "swapclasslevels":
                    await handle_swapclasslevels(client, player_id_and_params_csv=keywords[2])
                elif keywords[1] == "repost":
                    await handle_repost(message, player_tag=keywords[2])
                elif keywords[1] == "characterstatus":
                    await handle_character_status_change(client, player_id_and_params_csv=keywords[2])
            # ALL CHANNELS - ADMIN COMMANDS
            else:
                if keywords[1] == "inventoryadd":
                    await handle_add_to_inventory(message, player_id_and_params_csv=keywords[2])
        # NON-ADMIN COMMANDS
        # ALL CHANNELS
        if keywords[1] == "inventory":
            await handle_inventory_prompt(message.author)
        elif keywords[1] == "inventoryremove":
            await handle_remove_from_inventory_prompt(message, int(keywords[2]))
        return True
    return False


async def handle_refresh_player_message(client, player_ids_csv):
    player_data_list = utils.split_strip(player_ids_csv, ',')
    for player_tag in player_data_list:
        player_id = utils.strip_id_tag(player_tag)
        await charactersbridge.refresh_player_message(client, player_id)


# TODO: Do the same for the rest of the commands as for this function, meaning:
#  Add a model class for the input and documentation.
async def handle_addsession(client, message, session_data_csv):
    """
     Expected input for `session_data_csv`:
        1) Player ID - required.
            1.1) The first player is always taken as the Dungeon Master.
        2) Character name - required even for the Dungeon Master.
        3) Class name if the character is expected to level up => optional.
            3.1) If class name is not provided, the character's main class will be leveled up.
        Example raw input for 3 players:
        '@<1234> - Bob, @<5678> - Alice - Rogue, @<9012> - Dave'
    """
    id_to_data: dict[str, AddSessionData] = AddSessionData.id_to_data_from_command_input(session_data_csv)
    if characters.add_session(id_to_data):
        for player_id in id_to_data:
            await charactersbridge.refresh_player_message(client, player_id)
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_removesession(client, message, session_data_csv):
    id_to_data: dict[str, AddSessionData] = AddSessionData.id_to_data_from_command_input(session_data_csv)
    if characters.remove_session(id_to_data):
        for player_id in id_to_data:
            await charactersbridge.refresh_player_message(client, player_id)
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_addplayer(client, player_data_csv):
    player_data_list = utils.split_strip(player_data_csv, ',')
    player_id = utils.strip_id_tag(player_data_list[0])
    player_data_list.pop(0)
    characters.add_player(player_id, player_data_list)
    players_channel = client.get_channel(channelsprovider.get_characters_info_channel_id())
    new_player_message = await charactersbridge.send_player_message(players_channel, player_id)
    channelsprovider.set_player_message_id(player_id, new_player_message.id)


async def handle_addcharacter(client, data_csv):
    data_list = utils.split_strip(data_csv, ',')
    player_id = utils.strip_id_tag(data_list[0])
    data_list.pop(0)
    characters.add_character(player_id, data_list)
    await charactersbridge.refresh_player_message(client, player_id)


async def handle_deletecharacter(client, player_id_char_name_csv):
    player_id_to_character_name = utils.split_strip(player_id_char_name_csv, ',')
    player_id = utils.strip_id_tag(player_id_to_character_name[0])
    characters.delete_character(player_id, player_id_to_character_name[1])
    await charactersbridge.refresh_player_message(client, player_id)


async def handle_changename(client, player_id_names_csv):
    player_id_and_names = utils.split_strip(player_id_names_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_names[0])
    characters.change_character_name(player_id, player_id_and_names[1], player_id_and_names[2])
    await charactersbridge.refresh_player_message(client, player_id)


async def handle_swapclasslevels(client, player_id_and_params_csv):
    player_id_and_params = utils.split_strip(player_id_and_params_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_params[0])
    characters.swap_class_levels(
        player_id=player_id,
        character_name=player_id_and_params[1],
        class_to_remove_from=player_id_and_params[2],
        class_to_add_to=player_id_and_params[3]
    )
    await charactersbridge.refresh_player_message(client, player_id)


async def handle_repost(message, player_tag):
    player_id = utils.strip_id_tag(player_tag)
    new_player_message = await charactersbridge.send_player_message(message.channel, player_id)
    channelsprovider.set_player_message_id(player_id, new_player_message.id)


async def handle_add_to_inventory(message, player_id_and_params_csv):
    player_id_and_params = utils.split_strip(player_id_and_params_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_params[0])
    if characters.add_dummy_item_to_inventory(
        player_id=player_id,
        item_name=player_id_and_params[1],
        item_rarity=player_id_and_params[2],
        item_rarity_level=player_id_and_params[3]
    ):
        await message.channel.send(f"{player_id_and_params[1]} was added to <@{player_id}>")
    else:
        await message.channel.send(f"{player_id_and_params[1]} was not added to <@{player_id}>. Prompt may be wrong.")


async def handle_inventory_prompt(author):

    strings = characters.get_inventory_strings(author.id)
    if len(strings) <= 0:
        await author.send("*inventory is empty*")
        return

    async def send_message(string):
        return await author.send(string)

    await charactersbridge.send_inventory_messages(author, strings, send_message)


async def handle_remove_from_inventory_prompt(message, item_index):
    if characters.remove_item_by_index(message.author.id, item_index):
        await message.author.send(f"Item at {item_index} was subtracted.")
    else:
        await message.author.send("Item was not removed.")


async def handle_character_status_change(client, player_id_and_params_csv):
    player_id_and_params = utils.split_strip(player_id_and_params_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_params[0])
    await charactersbridge.update_character_status(
        client, player_id, character_name=player_id_and_params[1], status=player_id_and_params[2])
