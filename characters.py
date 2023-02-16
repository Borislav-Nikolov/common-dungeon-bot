import firebase
import json
import utils

from utils import *

PLAYER_FIELD_NAME = "name"
PLAYER_FIELD_COMMON_TOKENS = "common_tokens"
PLAYER_FIELD_UNCOMMON_TOKENS = "uncommon_tokens"
PLAYER_FIELD_RARE_TOKENS = "rare_tokens"
PLAYER_FIELD_VERY_RARE_TOKENS = "very_rare_tokens"
PLAYER_FIELD_LEGENDARY_TOKENS = "legendary_tokens"
PLAYER_FIELD_CHARACTERS = "characters"

CHARACTER_FIELD_NAME = "character_name"
CHARACTER_FIELD_LEVEL = "character_level"
CHARACTER_FIELD_CLASSES = "classes"
CHARACTER_FIELD_LAST_DM = "last_dm"
CHARACTER_FIELD_SESSIONS = "sessions_on_this_level"

CLASS_FIELD_NAME = "class_name"
CLASS_FIELD_LEVEL = "level"
CLASS_FIELD_IS_PRIMARY = "is_primary"


def hardinit_player(player_id: str, player_data_json: str):
    with open('characters.json', 'w') as characters:
        characters.write('{')
        characters.write(f'"{player_id}":')
        characters.write(player_data_json)
        characters.write("}")
    with open("characters.json", "r") as character:
        data = json.load(character)
        firebase.update_in_players(data)


def subtract_player_tokens_for_rarity(player_id, rarity: str, rarity_level: str) -> bool:
    player_data = firebase.get_player(player_id)
    token_field = __player_token_field_for_rarity(utils.__rarity_to_ordinal(rarity))
    tokens_to_subtract = utils.__tokens_per_rarity_number(rarity, rarity_level)
    available_tokens = player_data[token_field]
    if tokens_to_subtract <= available_tokens:
        player_data[token_field] = available_tokens - tokens_to_subtract
        update_player(player_id, player_data)
        return True
    return False


def get_up_to_date_player_message(player_id) -> str:
    player_data = firebase.get_player(player_id)
    player_string = f'<@{player_id}>\n' \
                    f'**{player_data[PLAYER_FIELD_NAME]}**:\n' \
                    f'Tokens: {player_data[PLAYER_FIELD_COMMON_TOKENS]} common, ' \
                    f'{player_data[PLAYER_FIELD_UNCOMMON_TOKENS]} uncommon, ' \
                    f'{player_data[PLAYER_FIELD_RARE_TOKENS]} rare, ' \
                    f'{player_data[PLAYER_FIELD_VERY_RARE_TOKENS]} very rare, ' \
                    f'{player_data[PLAYER_FIELD_LEGENDARY_TOKENS]} legendary'
    characters_string = '\n'
    counter = 1
    for character in player_data[PLAYER_FIELD_CHARACTERS]:
        characters_string += f'{counter}) {character[CHARACTER_FIELD_NAME]} - '
        for clazz in character[CHARACTER_FIELD_CLASSES]:
            characters_string += f'{clazz[CLASS_FIELD_NAME]} {clazz[CLASS_FIELD_LEVEL]} - '
        character_level = character[CHARACTER_FIELD_LEVEL]
        current_sessions = character[CHARACTER_FIELD_SESSIONS]
        characters_string += f'{current_sessions}/{utils.__sessions_to_next_level(character_level)} to level ' \
                             f'{character_level + 1}'
        if CHARACTER_FIELD_LAST_DM in character:
            characters_string += f' - Last DM: {character[CHARACTER_FIELD_LAST_DM]}'
        characters_string += '\n'
        counter += 1
    return f'{player_string}{characters_string}'


# $characters.addsession.<@1234>-PCName-OptClassName,<@1234>-PCName-OptClassName,<@1234>-PCName-OptClassName
def add_session(csv_data) -> bool:
    split_data = csv_data.split(',')
    print(split_data)
    player_id_to_character = {
        utils.__strip_id_tag(id_to_character[0:id_to_character.find('-')]): id_to_character[
                                                                            id_to_character.find('-') + 1:].split('-')
        for id_to_character in split_data
    }
    player_ids = list(map(lambda it: utils.__strip_id_tag(it if it.find('-') == -1 else it[0:it.find('-')]), split_data))
    players_data = firebase.get_players(player_ids)
    if len(players_data) != len(split_data):
        raise Exception("Invalid player data provided.")
    for player_id in players_data:
        player_data = players_data[player_id]
        character: dict = dict()
        for character_data in player_data[PLAYER_FIELD_CHARACTERS]:
            if character_data[CHARACTER_FIELD_NAME] == player_id_to_character[player_id][0]:
                character = character_data
                break
        if len(character) == 0:
            raise Exception(f"Character name not found for player {player_data[PLAYER_FIELD_NAME]}")
        # assign tokens
        player_data[PLAYER_FIELD_COMMON_TOKENS] += 1
        player_data[PLAYER_FIELD_UNCOMMON_TOKENS] += 1
        if character[CHARACTER_FIELD_LEVEL] >= 6:
            player_data[PLAYER_FIELD_RARE_TOKENS] += 1
        if character[CHARACTER_FIELD_LEVEL] >= 11:
            player_data[PLAYER_FIELD_VERY_RARE_TOKENS] += 1
        if character[CHARACTER_FIELD_LEVEL] >= 16:
            player_data[PLAYER_FIELD_LEGENDARY_TOKENS] += 1
        # level up if needed
        sessions_to_next_level = utils.__sessions_to_next_level(character[CHARACTER_FIELD_LEVEL])
        character[CHARACTER_FIELD_SESSIONS] += 1
        should_level_up = character[CHARACTER_FIELD_SESSIONS] >= int(sessions_to_next_level)
        leveled_up = False
        if should_level_up:
            character[CHARACTER_FIELD_LEVEL] += 1
            character[CHARACTER_FIELD_SESSIONS] = 0
            for clazz in character[CHARACTER_FIELD_CLASSES]:
                if len(player_id_to_character[player_id]) == 2 and player_id_to_character[player_id][1] ==\
                        clazz[CLASS_FIELD_NAME]:
                    clazz[CLASS_FIELD_LEVEL] += 1
                    leveled_up = True
                elif clazz[CLASS_FIELD_IS_PRIMARY] and len(player_id_to_character[player_id]) != 2:
                    clazz[CLASS_FIELD_LEVEL] += 1
                    leveled_up = True
        if not leveled_up and should_level_up:
            raise Exception("Invalid character class name provided.")
        # assign last DM
        is_game_master = player_id == player_ids[0]
        if not is_game_master:
            character[CHARACTER_FIELD_LAST_DM] = players_data[player_ids[0]][PLAYER_FIELD_NAME]
    # upload in database
    firebase.update_in_players(players_data)
    return True


def __player_token_field_for_rarity(rarity_ordinal: int) -> str:
    if rarity_ordinal == COMMON_ORDINAL:
        return PLAYER_FIELD_COMMON_TOKENS
    elif rarity_ordinal == UNCOMMON_ORDINAL:
        return PLAYER_FIELD_UNCOMMON_TOKENS
    elif rarity_ordinal == RARE_ORDINAL:
        return PLAYER_FIELD_RARE_TOKENS
    elif rarity_ordinal == VERY_RARE_ORDINAL:
        return PLAYER_FIELD_VERY_RARE_TOKENS
    elif rarity_ordinal == LEGENDARY_ORDINAL:
        return PLAYER_FIELD_LEGENDARY_TOKENS


def add_player_info_message_id(player_id, info_message_id):
    print("TODO")


# expected: <@1234>,name=SomeName,character=CharName,class=Rogue
def add_player(player_data):
    print("TODO")


def update_player_session(player_id: str, character_name: str, class_name: str):
    print("TODO")


def delete_player(player_id):
    print("TODO")


def update_player(player_id, player_data):
    all_data = dict()
    all_data[player_id] = player_data
    firebase.update_in_players(all_data)
