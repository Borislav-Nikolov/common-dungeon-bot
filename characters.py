import firebase
import json
import utils

from utils import *

PLAYER_FIELD_INFO_MESSAGE_ID = "info_message_id"
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
CHARACTER_FIELD_LAST_DM = "last_dm_id"
CHARACTER_FIELD_TOTAL_SESSIONS = "total_sessions"

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
    return f'<@{player_id}>\n' \
           f'**{player_data[PLAYER_FIELD_NAME]}**:\n' \
           f'Tokens: {player_data[PLAYER_FIELD_COMMON_TOKENS]} common, ' \
           f'{player_data[PLAYER_FIELD_UNCOMMON_TOKENS]} uncommon, ' \
           f'{player_data[PLAYER_FIELD_RARE_TOKENS]} rare, ' \
           f'{player_data[PLAYER_FIELD_VERY_RARE_TOKENS]} very rare, ' \
           f'{player_data[PLAYER_FIELD_LEGENDARY_TOKENS]} legendary'


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


# expected: <@1234>, <@2345>-CharName1, <@3456>-CharName2-Cleric...
def add_session(session_data):
    print("TODO")


def update_player_session(player_id: str, character_name: str, class_name: str):
    print("TODO")


def delete_player(player_id):
    print("TODO")


def update_player(player_id, player_data):
    all_data = dict()
    all_data[player_id] = player_data
    firebase.update_in_players(all_data)
