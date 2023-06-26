from controller import characters
from provider import channelsprovider
from util import utils, botutils


async def handle_character_commands(message, client):
    characters_key = '$characters'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == characters_key:
        # ADMIN COMMANDS
        if botutils.is_admin(message):
            # ALL CHANNELS
            if keywords[1] == "hardinit":
                await handle_hardinit(client, player_tag=keywords[2], json_data=keywords[3])
            # CHARACTERS INFO CHANNEL COMMANDS
            elif botutils.is_characters_info_channel(message):
                if keywords[1] == "addsession":
                    await handle_addsession(client, message, session_data_csv=keywords[2])
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
                    await handle_repost(client, player_tag=keywords[2])
        # NON-ADMIN COMMANDS
        else:
            # ALL CHANNELS
            if keywords[1] == "inventory":
                await handle_inventory_prompt(message)


async def handle_hardinit(client, player_tag, json_data):
    player_id = utils.strip_id_tag(player_tag)
    characters.hardinit_player(player_id, json_data)
    players_channel = client.get_channel(channelsprovider.get_characters_info_channel_id())
    await players_channel.send(characters.get_up_to_date_player_message(player_id))


async def handle_addsession(client, message, session_data_csv):
    if characters.add_session(session_data_csv):
        split_data = utils.split_strip(session_data_csv, ',')
        player_ids = list(
            map(lambda it: utils.strip_id_tag(it if it.find('-') == -1 else it[0:it.find('-')]), split_data))
        for player_id in player_ids:
            await characters.refresh_player_message(client, player_id)
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_addplayer(client, player_data_csv):
    player_data_list = utils.split_strip(player_data_csv, ',')
    player_id = utils.strip_id_tag(player_data_list[0])
    player_data_list.pop(0)
    characters.add_player(player_id, player_data_list)
    players_channel = client.get_channel(channelsprovider.get_characters_info_channel_id())
    new_player_message = await players_channel.send(characters.get_up_to_date_player_message(player_id))
    content = str(new_player_message.content)
    channelsprovider.set_player_message_id(utils.strip_id_tag(content), new_player_message.id)


async def handle_addcharacter(client, data_csv):
    data_list = utils.split_strip(data_csv, ',')
    player_id = utils.strip_id_tag(data_list[0])
    data_list.pop(0)
    characters.add_character(player_id, data_list)
    await characters.refresh_player_message(client, player_id)


async def handle_deletecharacter(client, player_id_char_name_csv):
    player_id_to_character_name = utils.split_strip(player_id_char_name_csv, ',')
    player_id = utils.strip_id_tag(player_id_to_character_name[0])
    characters.delete_character(player_id, player_id_to_character_name[1])
    await characters.refresh_player_message(client, player_id)


async def handle_changename(client, player_id_names_csv):
    player_id_and_names = utils.split_strip(player_id_names_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_names[0])
    characters.change_character_name(player_id, player_id_and_names[1], player_id_and_names[2])
    await characters.refresh_player_message(client, player_id)


async def handle_swapclasslevels(client, player_id_and_params_csv):
    player_id_and_params = utils.split_strip(player_id_and_params_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_params[0])
    characters.swap_class_levels(
        player_id=player_id,
        character_name=player_id_and_params[1],
        class_to_remove_from=player_id_and_params[2],
        class_to_add_to=player_id_and_params[3]
    )
    await characters.refresh_player_message(client, player_id)


async def handle_repost(message, player_tag):
    player_id = utils.strip_id_tag(player_tag)
    await message.channel.send(characters.get_up_to_date_player_message(player_id))


async def handle_inventory_prompt(message):
    inventory_string = characters.get_inventory_string(message.author.id)
    await message.author.send(inventory_string)
