import json
from provider import charactersprovider, channelsprovider
from util.itemutils import *
from model.player import Player
from model.character import Character
from model.inventoryitem import InventoryItem
from model.characterclass import CharacterClass


PARAMETER_NAME = "name"
PARAMETER_CHARACTER = "character"
PARAMETER_CLASS = "class"
PARAMETER_LEVEL = "level"


def hardinit_player(player_id: str, player_data_json: str):
    with open('../characters.json', 'w', encoding="utf-8") as characters:
        characters.write('{')
        characters.write(f'"{player_id}":')
        characters.write(player_data_json)
        characters.write("}")
    with open("../characters.json", "r") as character:
        data = json.load(character)
        charactersprovider.add_or_update_players_data(data)


def subtract_player_tokens_for_rarity(player_id, rarity: str, rarity_level: str) -> bool:
    player: Player = charactersprovider.get_player(player_id)
    tokens_to_subtract = utils.tokens_per_rarity_number(rarity, rarity_level)
    available_tokens = player.get_tokens_with_rarity_string(rarity)
    if tokens_to_subtract <= available_tokens:
        player.set_tokens_with_rarity_string(rarity, available_tokens - tokens_to_subtract)
        charactersprovider.add_or_update_player_data(player)
        return True
    return False


def add_item_to_inventory(player_id, new_item: InventoryItem):
    player: Player = charactersprovider.get_player(player_id)
    repeats = False
    for item in player.inventory:
        if new_item.name == item.name:
            repeats = True
            item.quantity += 1
    if not repeats:
        new_item.index = len(player.inventory) + 1
        new_item.quantity = 1
        player.inventory.append(new_item)
    charactersprovider.add_or_update_player_data(player)


def get_inventory_string(player_id) -> str:
    inventory = charactersprovider.get_player(player_id).inventory
    inventory_string = ""
    for item in inventory:
        inventory_string += get_unsold_item_row_string(magic_item=item)
    return inventory_string if len(inventory_string) != 0 else "*inventory is empty*"


def get_item_from_inventory(player_id, item_index) -> InventoryItem:
    inventory = charactersprovider.get_player(player_id).inventory
    for item in inventory:
        if item.index == item_index:
            return item
    raise Exception("Item was not found")


def refund_item_by_index(player_id, item_index: int) -> str:
    item: InventoryItem = get_item_from_inventory(player_id, item_index)
    player: Player = charactersprovider.get_player(player_id)
    subtracted = subtract_item_from_inventory(player, item)
    if subtracted:
        add_tokens_to_player_for_rarity(player, item.rarity.rarity, item.rarity.rarity_level)
        charactersprovider.add_or_update_player_data(player)
        return item.name
    return ""


def subtract_item_from_inventory(player: Player, item: InventoryItem) -> bool:
    subtracted = False
    removed = False
    list_index = 0
    for inventory_item in player.inventory:
        if inventory_item.index == item.index:
            inventory_item.quantity -= 1
            if inventory_item.quantity <= 0:
                player.inventory.pop(list_index)
                removed = True
            subtracted = True
            break
        list_index += 1
    if subtracted:
        if removed:
            new_item_index = 1
            for remaining_item in player.inventory:
                remaining_item.index = new_item_index
                new_item_index += 1
        return True
    return False


def add_player_tokens_for_rarity(player_id, rarity: str, rarity_level: str) -> bool:
    player: Player = charactersprovider.get_player(player_id)
    add_tokens_to_player_for_rarity(player, rarity, rarity_level)
    charactersprovider.add_or_update_player_data(player)
    return True


def add_tokens_to_player_for_rarity(player: Player, rarity: str, rarity_level: str):
    tokens_to_add = utils.tokens_per_rarity_number(rarity, rarity_level)
    current_tokens = player.get_tokens_with_rarity_string(rarity)
    player.set_tokens_with_rarity_string(rarity, current_tokens + tokens_to_add)


def get_up_to_date_player_message(player_id) -> str:
    player: Player = charactersprovider.get_player(player_id)
    player_string = f'<@{player.player_id}>\n' \
                    f'**Player:** {player.name}\n' \
                    f'**Tokens:** {player.common_tokens} common, ' \
                    f'{player.uncommon_tokens} uncommon, ' \
                    f'{player.rare_tokens} rare, ' \
                    f'{player.very_rare_tokens} very rare, ' \
                    f'{player.legendary_tokens} legendary'
    characters_string = '\n**Characters:**\n'
    counter = 1
    for character in player.characters:
        characters_string += f'{counter}) {character.character_name} - '
        class_index = 0
        for character_class in character.classes:
            characters_string += f'{character_class.class_name} {character_class.level}'
            if class_index != len(character.classes) - 1:
                characters_string += ' - '
            class_index += 1
        if character.character_level < 20:
            character_level = character.character_level
            current_sessions = character.sessions_on_this_level
            characters_string += f' - {current_sessions}/{utils.sessions_to_next_level(character_level)} to level ' \
                                 f'{character_level + 1}'
        characters_string += f' - Last DM: {character.last_dm}'
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
    players: list[Player] = charactersprovider.get_players(player_ids)
    if len(players) != len(split_data):
        raise Exception("Invalid player data provided.")
    dungeon_master = None
    # Find dungeon master
    for potential_dm in players:
        if potential_dm.player_id == player_ids[0]:
            dungeon_master = potential_dm
            break
    for player in players:
        character_loop_index = 0
        for character in player.characters:
            if character.character_name == player_id_to_character_and_class[player.player_id][0]:
                # assign tokens
                player.common_tokens += 1
                player.uncommon_tokens += 1
                if character.character_level >= 6:
                    player.rare_tokens += 1
                if character.character_level >= 11:
                    player.very_rare_tokens += 1
                if character.character_level >= 16:
                    player.legendary_tokens += 1
                # level up if needed
                if character.character_level < 20:
                    sessions_needed_for_next_level = utils.sessions_to_next_level(character.character_level)
                    character.sessions_on_this_level += 1
                    should_level_up = character.sessions_on_this_level >= sessions_needed_for_next_level
                    leveled_up = False
                    if should_level_up:
                        character.character_level += 1
                        character.sessions_on_this_level = 0
                        class_index = 0
                        for character_class in character.classes:
                            is_last_class = class_index == (len(character.classes) - 1)
                            has_class_param = len(player_id_to_character_and_class[player.player_id]) == 2
                            class_param = '' if not has_class_param\
                                else player_id_to_character_and_class[player.player_id][1]
                            if has_class_param and class_param == character_class.class_name:
                                character_class.level += 1
                                leveled_up = True
                            elif has_class_param and is_last_class:
                                add_class_to_character_data(character, {class_param: 1}, False)
                                leveled_up = True
                            elif character_class.is_primary and not has_class_param:
                                character_class.level += 1
                                leveled_up = True
                            if leveled_up:
                                break
                            class_index += 1
                    if not leveled_up and should_level_up:
                        raise Exception("Invalid character class name provided.")
                    # assign last DM
                    if player.player_id != dungeon_master.player_id:
                        character.last_dm = dungeon_master.name
                break
            character_loop_index += 1
            if character_loop_index >= (len(player.characters) - 1):
                raise Exception(f"Character name not found for player {player.name}")
    # upload in database
    charactersprovider.add_or_update_players_data(players)
    return True


# expected: player_id: <@1234> player_data_list: name=SomeName,character=CharName,class=Rogue
def add_player(player_id: str, player_data_list: list):
    # TODO: continue
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
    charactersprovider.add_or_update_players_data(player_data)


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
    player_data = charactersprovider.get_player(player_id)
    new_character = dict()
    new_character[CHARACTER_FIELD_NAME] = character_name
    new_character[CHARACTER_FIELD_LEVEL] = character_level
    new_character[CHARACTER_FIELD_LAST_DM] = 'no one yet'
    new_character[CHARACTER_FIELD_SESSIONS] = 0
    new_character[CHARACTER_FIELD_CLASSES] = list()
    add_class_to_character_data(new_character, classes_to_level, True)
    player_data[PLAYER_FIELD_CHARACTERS].append(new_character)
    update_player(player_id, player_data)


def delete_character(player_id, character_name):
    player_data = charactersprovider.get_player(player_id)
    index = -1
    for character in player_data[PLAYER_FIELD_CHARACTERS]:
        index += 1
        if character[CHARACTER_FIELD_NAME] == character_name:
            player_data[PLAYER_FIELD_CHARACTERS].pop(index)
            break
    update_player(player_id, player_data)


def change_character_name(player_id, old_name, new_name):
    player_data = charactersprovider.get_player(player_id)
    character = find_character_or_throw(player_data, old_name)
    character[CHARACTER_FIELD_NAME] = new_name
    update_player(player_id, player_data)


def swap_class_levels(player_id, character_name, class_to_remove_from, class_to_add_to):
    player_data = charactersprovider.get_player(player_id)
    character = find_character_or_throw(player_data, character_name)
    was_level_removed = False
    was_level_added = False
    for class_data in character[CHARACTER_FIELD_CLASSES]:
        class_name = class_data[CLASS_FIELD_NAME]
        if class_name == class_to_remove_from:
            if class_data[CLASS_FIELD_LEVEL] <= 1:
                raise Exception("Class to remove from must be of level higher than 1.")
            else:
                class_data[CLASS_FIELD_LEVEL] -= 1
                was_level_removed = True
        elif class_name == class_to_add_to:
            if class_data[CLASS_FIELD_LEVEL] >= 20:
                raise Exception("Class to add to must be of level lower than 20.")
            else:
                class_data[CLASS_FIELD_LEVEL] += 1
                was_level_added = True
    if not was_level_removed:
        raise Exception("Class to remove from was not found.")
    elif was_level_removed and not was_level_added:
        add_class_to_character_data(character, {class_to_add_to: 1}, False)
    update_player(player_id, player_data)


def find_character_or_throw(player_data, character_name) -> dict:
    for character in player_data[PLAYER_FIELD_CHARACTERS]:
        if character[CHARACTER_FIELD_NAME] == character_name:
            return character
    raise Exception("Character not found.")


def add_class_to_character_data(character: Character, classes_to_levels: dict, is_first_primary: bool):
    is_primary = is_first_primary
    for class_name in classes_to_levels:
        if not in_range(classes_to_levels[class_name], 1, 20):
            raise Exception('Class level is not in range.')
        elif len(class_name) == 0:
            raise Exception('Class name is empty.')
        new_character_class: CharacterClass = CharacterClass(
            class_name=class_name,
            level=classes_to_levels[class_name],
            is_primary=is_primary
        )
        if is_primary:
            is_primary = False
        character.classes.append(new_character_class)


async def refresh_player_message(client, player_id):
    await update_player_message(client, player_id, get_up_to_date_player_message(player_id))


async def update_player_message(client, player_id, new_message):
    players_channel = client.get_channel(channelsprovider.get_characters_info_channel_id())
    player_message_id = channelsprovider.get_player_message_id(player_id)
    player_message = await players_channel.fetch_message(player_message_id)
    await player_message.edit(content=new_message)
