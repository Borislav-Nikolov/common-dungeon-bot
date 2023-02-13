import firebase
import json
from firebase import set_in_players

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


def set_player(player_id: str, player_data_json: str) -> str:
    stripped_player_id = player_id.strip()[2:len(player_id) - 1]
    with open('characters.json', 'w') as characters:
        characters.write('{')
        characters.write(f'"{stripped_player_id}":')
        characters.write(player_data_json)
        characters.write("}")
    with open("characters.json", "r") as character:
        data = json.load(character)
        firebase.set_in_players(data)
        return player_id + "\n" + "there will be data here"


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
