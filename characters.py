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

PARAMETER_NAME = "name"
PARAMETER_CHARACTER = "character"
PARAMETER_CLASS = "class"
PARAMETER_LEVEL = "level"


def hardinit_player(player_id: str, player_data_json: str):
    with open('characters.json', 'w', encoding="utf-8") as characters:
        characters.write('{')
        characters.write(f'"{player_id}":')
        characters.write(player_data_json)
        characters.write("}")
    with open("characters.json", "r") as character:
        data = json.load(character)
        firebase.update_in_players(data)


def subtract_player_tokens_for_rarity(player_id, rarity: str, rarity_level: str) -> bool:
    player_data = firebase.get_player(player_id)
    token_field = player_token_field_for_rarity(utils.rarity_to_ordinal(rarity))
    tokens_to_subtract = utils.tokens_per_rarity_number(rarity, rarity_level)
    available_tokens = player_data[token_field]
    if tokens_to_subtract <= available_tokens:
        player_data[token_field] = available_tokens - tokens_to_subtract
        update_player(player_id, player_data)
        return True
    return False


def add_player_tokens_for_rarity(player_id, rarity: str, rarity_level: str) -> bool:
    player_data = firebase.get_player(player_id)
    token_field = player_token_field_for_rarity(utils.rarity_to_ordinal(rarity))
    tokens_to_add = utils.tokens_per_rarity_number(rarity, rarity_level)
    player_data[token_field] += tokens_to_add
    update_player(player_id, player_data)
    return True


def get_up_to_date_player_message(player_id) -> str:
    player_data = firebase.get_player(player_id)
    player_string = f'<@{player_id}>\n' \
                    f'**Player:** {player_data[PLAYER_FIELD_NAME]}\n' \
                    f'**Tokens:** {player_data[PLAYER_FIELD_COMMON_TOKENS]} common, ' \
                    f'{player_data[PLAYER_FIELD_UNCOMMON_TOKENS]} uncommon, ' \
                    f'{player_data[PLAYER_FIELD_RARE_TOKENS]} rare, ' \
                    f'{player_data[PLAYER_FIELD_VERY_RARE_TOKENS]} very rare, ' \
                    f'{player_data[PLAYER_FIELD_LEGENDARY_TOKENS]} legendary'
    characters_string = '\n**Characters:**\n'
    counter = 1
    for character in player_data[PLAYER_FIELD_CHARACTERS]:
        characters_string += f'{counter}) {character[CHARACTER_FIELD_NAME]} - '
        class_index = 0
        for clazz in character[CHARACTER_FIELD_CLASSES]:
            characters_string += f'{clazz[CLASS_FIELD_NAME]} {clazz[CLASS_FIELD_LEVEL]}'
            if class_index != len(character[CHARACTER_FIELD_CLASSES]) - 1:
                characters_string += ' - '
            class_index += 1
        if character[CHARACTER_FIELD_LEVEL] < 20:
            character_level = character[CHARACTER_FIELD_LEVEL]
            current_sessions = character[CHARACTER_FIELD_SESSIONS]
            characters_string += f' - {current_sessions}/{utils.sessions_to_next_level(character_level)} to level ' \
                                 f'{character_level + 1}'
        if CHARACTER_FIELD_LAST_DM in character:
            characters_string += f' - Last DM: {character[CHARACTER_FIELD_LAST_DM]}'
        characters_string += '\n'
        counter += 1
    return f'{player_string}{characters_string}'


# $characters.addsession.<@1234>-PCName-OptClassName,<@1234>-PCName-OptClassName,<@1234>-PCName-OptClassName
def add_session(csv_data) -> bool:
    split_data = split_strip(csv_data, ',')
    player_id_to_character_and_class = {
        utils.strip_id_tag(
            id_to_character[0:id_to_character.find('-')]
        ): split_strip(id_to_character[id_to_character.find('-') + 1:], '-')
        for id_to_character in split_data
    }
    player_ids = list(map(lambda it: utils.strip_id_tag(it if it.find('-') == -1 else it[0:it.find('-')]), split_data))
    players_data = firebase.get_players(player_ids)
    if len(players_data) != len(split_data):
        raise Exception("Invalid player data provided.")
    for player_id in players_data:
        player_data = players_data[player_id]
        character: dict = dict()
        for character_data in player_data[PLAYER_FIELD_CHARACTERS]:
            if character_data[CHARACTER_FIELD_NAME] == player_id_to_character_and_class[player_id][0]:
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
        if character[CHARACTER_FIELD_LEVEL] < 20:
            sessions_to_next_level_string = utils.sessions_to_next_level(character[CHARACTER_FIELD_LEVEL])
            character[CHARACTER_FIELD_SESSIONS] += 1
            should_level_up = character[CHARACTER_FIELD_SESSIONS] >= int(sessions_to_next_level_string)
            leveled_up = False
            if should_level_up:
                character[CHARACTER_FIELD_LEVEL] += 1
                character[CHARACTER_FIELD_SESSIONS] = 0
                for clazz in character[CHARACTER_FIELD_CLASSES]:
                    has_class_param = len(player_id_to_character_and_class[player_id]) == 2
                    class_param = '' if not has_class_param else player_id_to_character_and_class[player_id][1]
                    if has_class_param and class_param == clazz[CLASS_FIELD_NAME]:
                        clazz[CLASS_FIELD_LEVEL] += 1
                        leveled_up = True
                    elif has_class_param:
                        add_class_to_character_data(character, {class_param: 1})
                        leveled_up = True
                    elif clazz[CLASS_FIELD_IS_PRIMARY] and len(player_id_to_character_and_class[player_id]) != 2:
                        clazz[CLASS_FIELD_LEVEL] += 1
                        leveled_up = True
                    break
            if not leveled_up and should_level_up:
                raise Exception("Invalid character class name provided.")
        # assign last DM
        is_game_master = player_id == player_ids[0]
        if not is_game_master:
            character[CHARACTER_FIELD_LAST_DM] = players_data[player_ids[0]][PLAYER_FIELD_NAME]
    # upload in database
    firebase.update_in_players(players_data)
    return True


# expected: player_id: <@1234> player_data_list: name=SomeName,character=CharName,class=Rogue
def add_player(player_id: str, player_data_list: list):
    player_data = dict()
    player_data[player_id] = dict()
    player_name = ''
    character_name = ''
    character_class = ''
    for parameter in player_data_list:
        field_to_argument = split_strip(parameter, '=')
        field = field_to_argument[0]
        argument = field_to_argument[1]
        if field == PARAMETER_NAME:
            player_name = argument
        elif field == PARAMETER_CHARACTER:
            character_name = argument
        elif field == PARAMETER_CLASS:
            character_class = argument
    if len(player_name) == 0 or len(character_name) == 0 or len(character_class) == 0:
        raise Exception("Invalid new player input provided.")
    player_data[player_id][PLAYER_FIELD_NAME] = player_name
    class_data = dict()
    class_data[CLASS_FIELD_NAME] = character_class
    class_data[CLASS_FIELD_LEVEL] = 1
    class_data[CLASS_FIELD_IS_PRIMARY] = True
    character_data = dict()
    character_data[CHARACTER_FIELD_NAME] = character_name
    character_data[CHARACTER_FIELD_LEVEL] = 1
    character_data[CHARACTER_FIELD_SESSIONS] = 0
    character_data[CHARACTER_FIELD_LAST_DM] = "no one yet"
    character_data[CHARACTER_FIELD_CLASSES] = list()
    character_data[CHARACTER_FIELD_CLASSES].append(class_data)
    player_data[player_id][PLAYER_FIELD_CHARACTERS] = list()
    player_data[player_id][PLAYER_FIELD_CHARACTERS].append(character_data)
    player_data[player_id][PLAYER_FIELD_COMMON_TOKENS] = 0
    player_data[player_id][PLAYER_FIELD_UNCOMMON_TOKENS] = 0
    player_data[player_id][PLAYER_FIELD_RARE_TOKENS] = 0
    player_data[player_id][PLAYER_FIELD_VERY_RARE_TOKENS] = 0
    player_data[player_id][PLAYER_FIELD_LEGENDARY_TOKENS] = 0
    firebase.update_in_players(player_data)


# expected: player_id: <@1234> character_data_list: name=SomeName,class=Rogue,level=2
def add_character(player_id: str, character_data_list: list):
    character_name = ''
    character_level = 0
    classes_to_level = dict()
    for parameter in character_data_list:
        key_to_value = split_strip(parameter, '=')
        if key_to_value[0] == PARAMETER_NAME:
            character_name = key_to_value[1]
        elif key_to_value[0] == PARAMETER_CLASS:
            classes_to_level[key_to_value[1]] = 0
        elif key_to_value[0] == PARAMETER_LEVEL:
            for class_name in classes_to_level:
                if classes_to_level[class_name] == 0:
                    classes_to_level[class_name] = int(key_to_value[1])
                    character_level += int(key_to_value[1])
    if len(character_name.strip()) == 0 or len(classes_to_level) == 0:
        raise Exception('Invalid new character data provided')
    for class_name in classes_to_level:
        if classes_to_level[class_name] == 0 and len(classes_to_level) == 1:
            classes_to_level[class_name] = 1
            character_level += 1
        elif classes_to_level[class_name] == 0:
            raise Exception(f'Level not specified for class: {class_name}')
    player_data = firebase.get_player(player_id)
    new_character = dict()
    new_character[CHARACTER_FIELD_NAME] = character_name
    new_character[CHARACTER_FIELD_LEVEL] = character_level
    new_character[CHARACTER_FIELD_LAST_DM] = 'no one yet'
    new_character[CHARACTER_FIELD_SESSIONS] = 0
    new_character[CHARACTER_FIELD_CLASSES] = list()
    add_class_to_character_data(new_character, classes_to_level)
    player_data[PLAYER_FIELD_CHARACTERS].append(new_character)
    update_player(player_id, player_data)


def update_player(player_id, player_data):
    all_data = dict()
    all_data[player_id] = player_data
    firebase.update_in_players(all_data)


def player_token_field_for_rarity(rarity_ordinal: int) -> str:
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


def add_class_to_character_data(character_data: dict, classes_to_levels: dict):
    for class_name in classes_to_levels:
        if not in_range(classes_to_levels[class_name], 1, 20):
            raise Exception('Class level is not in range.')
        new_character_class = dict()
        new_character_class[CLASS_FIELD_NAME] = class_name
        new_character_class[CLASS_FIELD_LEVEL] = classes_to_levels[class_name]
        new_character_class[CLASS_FIELD_IS_PRIMARY] = True
        character_data[CHARACTER_FIELD_CLASSES].append(new_character_class)
