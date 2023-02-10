from firebase import set_in_players

PLAYER_FIELD_INFO_MESSAGE_ID = "info_message_id"
PLAYER_FIELD_NAME = "name"
PLAYER_FIELD_COMMON_TOKENS = "common_tokens"
PLAYER_FIELD_UNCOMMON_TOKENS = "uncommon_tokens"
PLAYER_FIELD_RARE_TOKENS = "rare_tokens"
PLAYER_FIELD_VERY_RARE_TOKENS = "very_rare_tokens"
PLAYER_FIELD_LEGENDARY_TOKENS = "legendary_tokens"
PLAYER_FIELD_CHARACTERS = "characters"

CHARACTER_FIELD_NAME = "name"
CHARACTER_FIELD_LEVEL = "level"
CHARACTER_FIELD_CLASSES = "classes"
CHARACTER_FIELD_LAST_DM = "last_dm_id"
CHARACTER_FIELD_TOTAL_SESSIONS = "total_sessions"

CLASS_FIELD_NAME = "name"
CLASS_FIELD_LEVEL = "level"
CLASS_FIELD_IS_PRIMARY = "is_primary"


# expected: <@1234>,name=SomeName,common_tokens=3,...,characters=name=CharName,level=2,classes=name=Rogue,level=1...
def set_player(player_data):
    print("start")
    parameters_list = player_data.split(';')
    player_object = dict()
    player_id = parameters_list[0].strip()
    print(f"Player id: {player_id}")
    if player_id.find('=') != -1 or player_id.find('<@') != 0 or player_id.find('>') != len(player_id) - 1:
        raise Exception(f'{player_id} is not a player ID.')
    player_object[player_id] = dict()
    player_contents = player_object[player_id]
    parameters_list.pop(0)
    for parameter in parameters_list:
        populate_from_parameters(player_contents, parameter.split(','))
    print(player_object)
    set_in_players(player_object)


def populate_from_parameters(dictionary, parameters):
    first_equality_index = parameters[0].find('=')
    inner_data_key = "uninitialized"
    inner_data = dict()
    if first_equality_index != parameters[0].rfind('='):
        offset = first_equality_index + 1
        inner_data_key = parameters[0][0:offset]
        first_parameter = parameters[0][offset:]
        parameters.pop(0)
        parameters.append(first_parameter)
        dictionary[inner_data_key] = inner_data
    for parameter in parameters:
        parameter = parameter.strip()
        entry = parameter.split('=')
        key = entry[0]
        value = entry[1]
        if inner_data_key in dictionary:
            inner_data[key] = value
        else:
            dictionary[key] = value


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
