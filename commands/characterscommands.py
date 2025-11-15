from typing import Optional
from datetime import datetime, timedelta
import asyncio

from controller import characters
from util import utils, botutils, itemutils, requestutils, timeutils
from model.addsessiondata import AddSessionData
from model.addplayerdata import AddPlayerData
from model.addcharacterdata import AddCharacterData
from model.playerstatus import player_status_from_name, PlayerStatus
from model.playerrole import player_role_from_name
from model.sessionlog import SessionLog
from bridge import charactersbridge
from api import charactersrequests, channelsrequests, logsrequests
from provider import charactersprovider


async def handle_character_commands(message, client) -> bool:
    characters_key = '$characters'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == characters_key:
        # ADMIN COMMANDS
        if botutils.is_admin_message(message):
            # CHARACTERS INFO CHANNEL
            if botutils.is_characters_info_channel(message):
                if keywords[1] == "addsession":
                    await handle_addsession(message, session_data_csv=keywords[2])
                elif keywords[1] == "removesession":
                    await handle_removesession(client, message, session_data_csv=keywords[2])
                elif keywords[1] == "refreshmessage":
                    await handle_refresh_player_message(client, player_ids_csv=keywords[2])
                elif keywords[1] == "addplayer":
                    await handle_addplayer(client, message, player_data_csv=keywords[2])
                elif keywords[1] == "addcharacter":
                    await handle_addcharacter(client, message, data_csv=keywords[2])
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
                elif keywords[1] == "changeid":
                    await handle_change_id(client, player_ids_csv=keywords[2])
            # ALL CHANNELS - ADMIN COMMANDS
            if keywords[1] == "inventoryadd":
                await handle_add_to_inventory(message, player_id_and_params_csv=keywords[2])
            elif keywords[1] == "changeplayerstatus":
                await handle_change_player_status(message, player_id_and_new_status_csv=keywords[2])
            elif keywords[1] == "changeplayerrole":
                await handle_change_player_role(message, player_id_and_new_role_csv=keywords[2])
            elif keywords[1] == "setallasactive":
                await handle_set_all_as_active()
            elif keywords[1] == "subtracttokensforrarity":
                await handle_subtract_tokens_for_rarity(message, player_id_and_params_csv=keywords[2])
            elif keywords[1] == "addmissingbundles":
                await handle_add_missing_bundles(message, player_tag=keywords[2])
            elif keywords[1] == "addtokens":
                await handle_add_arbitrary_tokens(message, data_csv=keywords[2])
            elif keywords[1] == "subtracttokens":
                await handle_subtract_arbitrary_tokens(message, data_csv=keywords[2])
        # NON-ADMIN COMMANDS
        # ALL CHANNELS
        if keywords[1] == "inventory":
            await handle_inventory_prompt(message.author)
        elif keywords[1] == "inventoryremove":
            await handle_remove_from_inventory_prompt(message, int(keywords[2]))
        elif keywords[1] == "maxlevel":
            await handle_set_max_level(message, keywords[2])
        elif keywords[1] == "generatelogmessage":
            await handle_generate_log_message(client, message, keywords[2])
        return True
    return False


async def handle_refresh_player_message(client, player_ids_csv):
    player_data_list = utils.split_strip(player_ids_csv, ',')
    for player_tag in player_data_list:
        player_id = utils.strip_id_tag(player_tag)
        await charactersbridge.refresh_player_message(client, player_id)


# TODO: Do the same for the rest of the commands as for this function, meaning:
#  Add a model class for the input and documentation.
async def handle_addsession(message, session_data_csv):
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
    if charactersrequests.make_add_session_request(id_to_data, message.author.global_name):
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_removesession(client, message, session_data_csv):
    id_to_data: dict[str, AddSessionData] = AddSessionData.id_to_data_from_command_input(session_data_csv)
    if charactersrequests.make_remove_session_request(id_to_data, message.author.global_name):
        for player_id in id_to_data:
            await charactersbridge.refresh_player_message(client, player_id)
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_addplayer(client, message, player_data_csv):
    player_data_list = utils.split_strip(player_data_csv, ',')
    player_id = utils.strip_id_tag(player_data_list[0])
    player_data_list.pop(0)

    add_player_data = AddPlayerData.from_command(player_id=player_id, player_data_list=player_data_list)
    if charactersrequests.make_add_player_request(add_player_data, message.author.global_name):
        players_channel = client.get_channel(channelsrequests.get_characters_info_channel_id())
        new_player_message = await charactersbridge.send_player_message(players_channel, player_id)
        channelsrequests.set_player_message_id(player_id, new_player_message.id)
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_addcharacter(client, message, data_csv):
    data_list = utils.split_strip(data_csv, ',')
    player_id = utils.strip_id_tag(data_list[0])
    data_list.pop(0)
    add_character_data = AddCharacterData.from_command(player_id, data_list)
    if charactersrequests.make_add_character_request(add_character_data, message.author.global_name):
        await charactersbridge.refresh_player_message(client, player_id)
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_deletecharacter(client, player_id_char_name_csv):
    player_id_to_character_name = utils.split_strip(player_id_char_name_csv, ',')
    player_id = utils.strip_id_tag(player_id_to_character_name[0])
    charactersrequests.make_delete_character_request(player_id, player_id_to_character_name[1])
    await charactersbridge.refresh_player_message(client, player_id)


async def handle_changename(client, player_id_names_csv):
    player_id_and_names = utils.split_strip(player_id_names_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_names[0])
    charactersrequests.make_change_character_name_request(player_id, player_id_and_names[1], player_id_and_names[2])
    await charactersbridge.refresh_player_message(client, player_id)


async def handle_swapclasslevels(client, player_id_and_params_csv):
    player_id_and_params = utils.split_strip(player_id_and_params_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_params[0])
    charactersrequests.make_swap_character_class_levels_request(
        player_id=player_id,
        character_name=player_id_and_params[1],
        class_to_remove_from=player_id_and_params[2],
        class_to_add_to=player_id_and_params[3]
    )
    await charactersbridge.refresh_player_message(client, player_id)


async def handle_repost(message, player_tag):
    player_id = utils.strip_id_tag(player_tag)
    new_player_message = await charactersbridge.send_player_message(message.channel, player_id)
    channelsrequests.set_player_message_id(player_id, new_player_message.id)
    charactersrequests.make_change_player_status_request(player_id, PlayerStatus.Active)


async def handle_add_to_inventory(message, player_id_and_params_csv):
    player_id_and_params = utils.split_strip(player_id_and_params_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_params[0])
    if characters.add_dummy_item_to_inventory(
        player_id=player_id,
        item_name=player_id_and_params[1],
        item_rarity=player_id_and_params[2],
        item_rarity_level=player_id_and_params[3],
        sellable=itemutils.str_to_is_sellable(player_id_and_params[4]) if len(player_id_and_params) >= 5 else False
    ):
        await message.channel.send(f"{player_id_and_params[1]} was added to <@{player_id}>")
    else:
        await message.channel.send(f"{player_id_and_params[1]} was not added to <@{player_id}>. Prompt may be wrong.")


async def handle_subtract_tokens_for_rarity(message, player_id_and_params_csv):
    player_id_and_params = utils.split_strip(player_id_and_params_csv, ',')
    player_id = utils.strip_id_tag(player_id_and_params[0])
    if characters.subtract_player_tokens_for_rarity(
        player_id=player_id,
        rarity=player_id_and_params[1],
        rarity_level=player_id_and_params[2]
    ):
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_inventory_prompt(author):

    strings = characters.get_inventory_strings(author.id)
    if len(strings) <= 0:
        await author.send("*inventory is empty*")
        return

    async def send_message(string):
        return await author.send(string)

    await charactersbridge.send_inventory_messages(author, strings, send_message)


async def handle_reserved_item_prompt(author):

    item_string = characters.get_reserved_item_string(author.id)
    if not item_string:
        await author.send("*you have no reserved items*")
        return

    async def send_message(string):
        return await author.send(string)

    await charactersbridge.send_reserved_item_message(author, item_string, send_message)


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


async def handle_change_id(client, player_ids_csv):
    player_data_list = utils.split_strip(player_ids_csv, ',')
    old_id = utils.strip_id_tag(player_data_list[0])
    new_id = utils.strip_id_tag(player_data_list[1])
    characters.change_player_id(old_id, new_id)
    player_message_id = channelsrequests.get_player_message_id(str(old_id))
    channelsrequests.set_player_message_id(str(new_id), player_message_id)
    channelsrequests.delete_player_message_id(str(old_id))
    await charactersbridge.refresh_player_message(client, new_id)


async def handle_change_player_status(message, player_id_and_new_status_csv):
    data_list = utils.split_strip(player_id_and_new_status_csv, ',')
    player_id = utils.strip_id_tag(data_list[0])
    new_player_status = data_list[1]
    if charactersrequests.make_change_player_status_request(player_id, player_status_from_name(new_player_status)):
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_change_player_role(message, player_id_and_new_role_csv):
    data_list = utils.split_strip(player_id_and_new_role_csv, ',')
    player_id = utils.strip_id_tag(data_list[0])
    new_player_role = data_list[1]
    if charactersrequests.make_change_player_role_request(player_id, player_role_from_name(new_player_role)):
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_set_all_as_active():
    all_players = charactersprovider.get_all_players()
    for player in all_players:
        charactersrequests.make_change_player_status_request(player.player_id, PlayerStatus.Active)


async def handle_set_max_level(message, character_name_and_max_level_csv):
    player_id = message.author.id
    name_and_max_lvl = utils.split_strip(character_name_and_max_level_csv, ',')
    if charactersrequests.make_set_character_max_level_request(
        player_id=player_id,
        character_name=name_and_max_lvl[0],
        max_level=name_and_max_lvl[1]
    ):
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_add_missing_bundles(message, player_tag):
    player_id = utils.strip_id_tag(player_tag)
    if charactersrequests.make_add_missing_bundles_request(player_id):
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')


async def handle_add_arbitrary_tokens(message, data_csv):
    data_list = utils.split_strip(data_csv, ',')
    player_id: str = utils.strip_id_tag(data_list[0])
    token_rarity: str = requestutils.translate_rarity_name(data_list[1])
    quantity_str = data_list[2]
    quantity: int = -1
    if quantity_str.isdigit():
        quantity = int(quantity_str)
    if len(token_rarity) > 0 and quantity >= 0:
        if charactersrequests.make_add_arbitrary_tokens_request(
            player_id=player_id,
            token_rarity=token_rarity,
            quantity=quantity,
            moderator_name=message.author.global_name
        ):
            await message.add_reaction('🪙')
        else:
            await message.add_reaction('❌')
    else:
        await message.add_reaction('❌')


async def handle_subtract_arbitrary_tokens(message, data_csv):
    data_list = utils.split_strip(data_csv, ',')
    player_id: str = utils.strip_id_tag(data_list[0])
    token_rarity: str = requestutils.translate_rarity_name(data_list[1])
    quantity_str = data_list[2]
    quantity: int = -1
    if quantity_str.isdigit():
        quantity = int(quantity_str)
    if len(token_rarity) > 0 and quantity >= 0:
        if charactersrequests.make_subtract_arbitrary_tokens_request(
            player_id=player_id,
            token_rarity=token_rarity,
            quantity=quantity,
            moderator_name=message.author.global_name
        ):
            await message.add_reaction('🪙')
        else:
            await message.add_reaction('❌')
    else:
        await message.add_reaction('❌')


async def handle_generate_log_message(client, message, data_str):
    # Attempt to extract datetime
    try:
        date_and_time = utils.split_strip(data_str, ' ')
        if len(date_and_time) == 1:
            parsed_datetime = timeutils.parse_date_str(date_and_time[0])
        else:
            parsed_datetime = timeutils.parse_datetime_str(data_str)
    except ValueError:
        parsed_datetime = None

    if parsed_datetime:
        await _generate_log_message_from_date(client, message, parsed_datetime.date())
    else:
        await _generate_log_message_from_csv_data(client, message, data_str)


async def _generate_log_message_from_date(client, message, target_date):
    day_before = target_date - timedelta(days=1)
    day_after = target_date + timedelta(days=1)

    start_datetime = datetime.combine(day_before, datetime.min.time())
    end_datetime = datetime.combine(day_after, datetime.max.time())

    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(end_datetime.timestamp())

    logs = logsrequests.get_session_logs_range(start_timestamp, end_timestamp)

    if len(logs) == 0:
        await message.add_reaction('❌')
        return

    if len(logs) == 1:
        # Extract the single log
        log_data = next(iter(logs.values()))
        session_log = SessionLog.from_dict(log_data)
        await _generate_log_message_from_log(client, message, session_log)
    else:
        # Multiple logs found - present options to user
        # Parse all logs once and store them
        parsed_logs = [(timestamp, SessionLog.from_dict(log_data)) for timestamp, log_data in logs.items()]

        # Collect all unique player IDs from all logs
        all_player_ids = set()
        for timestamp, session_log in parsed_logs:
            for player_data in session_log.players.values():
                all_player_ids.add(player_data.player_id)

        # Batch fetch all players at once
        players_cache = charactersprovider.get_players(
            list(all_player_ids),
            include_inventory=False,
            include_characters=False
        )

        # Build the message with numbered list
        response_lines = ["Multiple sessions found for this date. Please select one by replying with the number:"]
        for idx, (timestamp, session_log) in enumerate(parsed_logs, start=1):
            character_names = [
                (f'{players_cache[player_data.player_id].name} - '
                 f'{player_data.character_name}'
                 f'{' (DM)' if player_data.is_dm else ''}') for player_data in session_log.players.values()
            ]
            characters_str = ", ".join(character_names)
            response_lines.append(f"{idx}. {characters_str}")

        await message.channel.send("\n".join(response_lines))

        # Wait for user response
        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            user_response = await client.wait_for('message', timeout=60.0, check=check)
            selected_number = int(user_response.content.strip())

            if 1 <= selected_number <= len(parsed_logs):
                selected_session_log = parsed_logs[selected_number - 1][1]  # Get SessionLog from tuple
                await _generate_log_message_from_log(client, user_response, selected_session_log)
            else:
                await message.channel.send("Invalid selection. Please use the command again.")
        except ValueError:
            await message.channel.send("Invalid input. Please use the command again.")
        except asyncio.TimeoutError:
            await message.channel.send("Selection timed out. Please use the command again.")


async def _generate_log_message_from_log(client, message, session_log: SessionLog):
    # Build the data_csv string in the format: "player_id1-character1, player_id2-character2, ..."
    data_parts = []
    for player_id, player_data in session_log.players.items():
        data_parts.append(f"<@{player_data.player_id}>-{player_data.character_name}")

    if len(data_parts) > 0:
        data_csv = ', '.join(data_parts)
        # Call the existing handle_generate_log_message function
        await _generate_log_message_from_csv_data(client, message, data_csv)
    else:
        # No valid player data found in the log
        await message.add_reaction('❌')


async def _generate_log_message_from_csv_data(client, message, data_csv):
    data_list = utils.split_strip(data_csv, ',')
    character_to_player_id: dict[str, str] = dict()
    characters_list = list()
    for player_id_to_character in data_list:
        player_to_character_list = utils.split_strip(player_id_to_character, '-')
        character_to_player_id[player_to_character_list[1]] = player_to_character_list[0]
        characters_list.append(player_to_character_list[1])
    character_to_forum_posts: dict[str, Optional[str]] = await botutils.search_forum_titles(
        bot=client,
        forum_channel_id=channelsrequests.get_characters_forum_channel_id(),
        search_terms=characters_list,
        case_sensitive=False,
        prefer_exact_match=True
    )
    player_id_to_character_and_link: dict[str, dict[str, Optional[str]]] = dict()
    for character, link in character_to_forum_posts.items():
        player_id_to_character_and_link[character_to_player_id[character]] = {character: link}
    if len(player_id_to_character_and_link) > 0:
        await message.channel.send(characters.get_log_message(player_id_to_character_and_link))
    else:
        await message.add_reaction('❌')
