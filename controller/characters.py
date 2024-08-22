import discord

from provider import charactersprovider, channelsprovider
from util.itemutils import *
from model.player import Player
from model.character import Character
from model.inventoryitem import InventoryItem
from model.characterclass import CharacterClass
from model.addsessiondata import AddSessionData
from model.inventorymessage import InventoryMessage
from model.rarity import rarity_strings_to_rarity
from typing import Optional
from util import charactersutils


PARAMETER_NAME = "name"
PARAMETER_CHARACTER = "character"
PARAMETER_CLASS = "class"
PARAMETER_LEVEL = "level"


def update_character_status(player_id, character_name: str, status: str) -> bool:
    if not charactersutils.is_character_status_valid(status):
        return False
    player: Player = charactersprovider.get_player(player_id)
    character: Character = find_character_or_throw(player, character_name)
    character.status = status
    charactersprovider.add_or_update_player(player)
    return True


def subtract_player_tokens_for_rarity(player_id, rarity: str, rarity_level: str) -> bool:
    player: Player = charactersprovider.get_player(player_id)
    tokens_to_subtract = utils.tokens_per_rarity_number(rarity, rarity_level)
    available_tokens = player.get_tokens_with_rarity_string(rarity)
    if tokens_to_subtract <= available_tokens:
        player.set_tokens_with_rarity_string(rarity, available_tokens - tokens_to_subtract)
        charactersprovider.add_or_update_player(player)
        return True
    return False


def add_dummy_item_to_inventory(player_id, item_name, item_rarity, item_rarity_level) -> bool:
    rarity = rarity_strings_to_rarity(item_rarity, item_rarity_level)
    if rarity is None:
        return False
    add_single_quantity_item_to_inventory(
        player_id=player_id,
        new_item=InventoryItem(
                    name=item_name,
                    description="*dummy item has no description*",
                    price="*dummy item has no price in gold*",
                    rarity=rarity,
                    attunement=True,
                    consumable=False,
                    official=False,
                    banned=True,
                    quantity=1,
                    index=0
                )
    )
    return True


def add_single_quantity_item_to_inventory(player_id, new_item: InventoryItem):
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
    charactersprovider.add_or_update_player(player)


def get_inventory_strings(player_id) -> list[dict[int, str]]:
    player = charactersprovider.get_player(player_id)
    if fix_inventory(player):
        # refresh player reference if there were changes
        player = charactersprovider.get_player(player_id)
    inventory = player.inventory
    inventory_string = ""
    count = 0
    count_to_string = list()
    for item in inventory:
        count += 1
        inventory_string += get_inventory_item_row_string(magic_item=item)
        if count % 20 == 0 or count == len(inventory):
            count_to_string.append({20 if count % 20 == 0 else count % 20: inventory_string})
            inventory_string = ""
    return count_to_string


def set_inventory_messages(player_id, inventory_messages: list[InventoryMessage]):
    player = charactersprovider.get_player(player_id)
    player.inventory_messages = inventory_messages
    charactersprovider.add_or_update_player(player)


def get_inventory_messages(player_id) -> list[InventoryMessage]:
    return charactersprovider.get_player(player_id).inventory_messages


def get_inventory_item_by_reaction_index(item_index_relative, message_id, player_id) -> Optional[InventoryItem]:
    player = charactersprovider.get_player(player_id)
    for inventory_message in player.inventory_messages:
        if inventory_message.message_id == message_id:
            item_index = inventory_message.beginning_index + (item_index_relative - 1)
            try:
                return get_item_from_inventory(player, item_index)
            except ValueError:
                return None
    raise ValueError("Inventory message not found.")


def refresh_inventory_by_id_if_needed(player_id) -> bool:
    return refresh_inventory_if_needed(charactersprovider.get_player(player_id))


def refresh_inventory_if_needed(player: Player) -> bool:
    last_item = None
    needs_refresh = False
    for item in player.inventory:
        if last_item is not None:
            difference = item.index - last_item.index
            if difference != 1:
                needs_refresh = True
                break
        last_item = item
    if needs_refresh:
        new_index = 1
        for item in player.inventory:
            item.index = new_index
            new_index += 1
    return needs_refresh


def fix_inventory(player: Player) -> bool:
    if refresh_inventory_if_needed(player):
        charactersprovider.add_or_update_player(player)
        return True
    return False


def get_item_from_inventory(player: Player, item_index) -> InventoryItem:
    inventory = player.inventory
    for item in inventory:
        if item.index == item_index:
            return item
    raise ValueError("Item was not found")


def get_item_from_inventory_by_id(player_id, item_index) -> InventoryItem:
    return get_item_from_inventory(charactersprovider.get_player(player_id), item_index)


def refund_item_by_index(player_id, item_index: int) -> str:
    item: InventoryItem = get_item_from_inventory_by_id(player_id, item_index)
    player: Player = charactersprovider.get_player(player_id)
    subtracted = subtract_item_from_inventory(player, item)
    if subtracted:
        add_tokens_to_player_for_rarity(player, item.rarity.rarity, item.rarity.rarity_level)
        charactersprovider.add_or_update_player(player)
        return item.name
    return ""


def remove_item_by_index(player_id, item_index: int) -> bool:
    item: InventoryItem = get_item_from_inventory_by_id(player_id, item_index)
    player: Player = charactersprovider.get_player(player_id)
    subtracted = subtract_item_from_inventory(player, item)
    if subtracted:
        charactersprovider.add_or_update_player(player)
    return subtracted


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
    charactersprovider.add_or_update_player(player)
    return True


def add_tokens_to_player_for_rarity(player: Player, rarity: str, rarity_level: str):
    tokens_to_add = utils.tokens_per_rarity_number(rarity, rarity_level)
    current_tokens = player.get_tokens_with_rarity_string(rarity)
    player.set_tokens_with_rarity_string(rarity, current_tokens + tokens_to_add)


def get_up_to_date_player_message(player_id) -> str:
    player: Player = charactersprovider.get_player(player_id)
    level = player.player_level
    player_string = f'<@{player.player_id}>\n' \
                    f'**Player:** {player.name}\n' \
                    f'**Level:** {level} - {player.sessions_on_this_level}/6 to level {level + 1}\n' \
                    f'**Tokens:** {player.common_tokens} common, ' \
                    f'{player.uncommon_tokens} uncommon, ' \
                    f'{player.rare_tokens} rare, ' \
                    f'{player.very_rare_tokens} very rare, ' \
                    f'{player.legendary_tokens} legendary'
    characters_string = '\n**Characters:**\n'
    for character in player.characters:
        characters_string += f'{charactersutils.status_emoji(character.status)} {character.character_name} - '
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
    return f'{player_string}{characters_string}'


def remove_session(player_id_to_data: dict[str, AddSessionData]) -> bool:
    player_ids = list(player_id_to_data.keys())
    players: list[Player] = charactersprovider.get_players(player_ids)
    if len(players) != len(player_ids):
        raise Exception("Invalid player data provided.")
    for player in players:
        if player.sessions_on_this_level == 0:
            player.player_level -= 1
            player.sessions_on_this_level = 5
        else:
            player.sessions_on_this_level -= 1
        for character in player.characters:
            # find character
            if character.character_name == player_id_to_data[player.player_id].character_name:
                if character.character_level == 1:
                    raise Exception(f"Level 1 character {character.character_name} cannot lose a session.")
                # determine level before previous session
                should_remove_level = character.sessions_on_this_level == 0
                previous_level = (character.character_level - 1) if should_remove_level else character.character_level
                character.character_level = previous_level
                # re-adjust current sessions
                current_sessions = (utils.sessions_to_next_level(
                    previous_level) if should_remove_level else character.sessions_on_this_level) - 1
                character.sessions_on_this_level = current_sessions
                # de-assign tokens
                player.common_tokens -= get_common_tokens(previous_level)
                player.uncommon_tokens -= get_uncommon_tokens(previous_level)
                player.rare_tokens -= get_rare_tokens(previous_level)
                player.very_rare_tokens -= get_very_rare_tokens(previous_level)
                player.legendary_tokens -= get_legendary_tokens(previous_level)
                if should_remove_level:
                    # determine class to remove level from
                    default_class = ''
                    default_class_level = -1
                    class_counter = 0
                    total_classes = len(character.classes)
                    has_class_param = player_id_to_data[player.player_id].class_name is not None
                    class_param = '' if not has_class_param else player_id_to_data[player.player_id].class_name
                    for character_class in character.classes:
                        class_counter += 1
                        if character_class.class_name == class_param:
                            character_class.level -= 1
                            if character_class.level == 0:
                                # remove class from character
                                class_index = utils.find_index(
                                    character.classes,
                                    lambda it: it.class_name == character_class.class_name
                                )
                                character.classes.pop(class_index)
                                break
                        if character_class.is_primary:
                            default_class = character_class.class_name
                            default_class_level = character_class.level
                        if class_counter == total_classes:
                            if len(class_param) != 0:
                                raise Exception(f"Class was not found: {class_param}")
                            if default_class_level < 2:
                                raise Exception(f"Default class of level 1 cannot be removed.")
                            # remove level from default class
                            default_class_index = utils.find_index(
                                character.classes,
                                lambda it: it.class_name == default_class
                            )
                            default_class_object = character.classes[default_class_index]
                            default_class_object.level -= 1
    # upload in database
    charactersprovider.add_or_update_players(players)
    return True


def add_session(player_id_to_data: dict[str, AddSessionData]) -> bool:
    player_ids = list(player_id_to_data.keys())
    players: list[Player] = charactersprovider.get_players(player_ids)
    if len(players) != len(player_ids):
        raise Exception("Invalid player data provided.")
    dungeon_master = None
    # Find dungeon master
    for potential_dm in players:
        if player_id_to_data[potential_dm.player_id].is_dm:
            dungeon_master = potential_dm
            break
    for player in players:
        if player.sessions_on_this_level == 5:
            player.player_level += 1
            player.sessions_on_this_level = 0
        else:
            player.sessions_on_this_level += 1
        character_loop_index = 0
        for character in player.characters:
            if character.character_name == player_id_to_data[player.player_id].character_name:
                # assign tokens
                player.common_tokens += get_common_tokens(character.character_level)
                player.uncommon_tokens += get_uncommon_tokens(character.character_level)
                player.rare_tokens += get_rare_tokens(character.character_level)
                player.very_rare_tokens += get_very_rare_tokens(character.character_level)
                player.legendary_tokens += get_legendary_tokens(character.character_level)
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
                            has_class_param = player_id_to_data[player.player_id].class_name is not None
                            class_param = '' if not has_class_param else player_id_to_data[player.player_id].class_name
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
            if character_loop_index > (len(player.characters) - 1):
                raise Exception(f"Character name not found for player {player.name}")
    # upload in database
    charactersprovider.add_or_update_players(players)
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
    charactersprovider.add_or_update_player(
        Player(
            player_id=player_id,
            name=player_name,
            player_level=1,
            sessions_on_this_level=0,
            common_tokens=0,
            uncommon_tokens=0,
            rare_tokens=0,
            very_rare_tokens=0,
            legendary_tokens=0,
            characters=[Character(
                character_name=character_name,
                character_level=1,
                classes=[CharacterClass(
                    class_name=character_class,
                    level=1,
                    is_primary=True
                )],
                last_dm="no one yet",
                sessions_on_this_level=0
            )],
            inventory=list[InventoryItem](),
            inventory_messages=list()
        )
    )


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
    player: Player = charactersprovider.get_player(player_id)
    new_character = Character(
        character_name=character_name,
        character_level=character_level,
        classes=list[CharacterClass](),
        last_dm='no one yet',
        sessions_on_this_level=0
    )
    add_class_to_character_data(new_character, classes_to_level, True)
    player.characters.append(new_character)
    charactersprovider.add_or_update_player(player)


def delete_character(player_id, character_name):
    player: Player = charactersprovider.get_player(player_id)
    index = -1
    for character in player.characters:
        index += 1
        if character.character_name == character_name:
            player.characters.pop(index)
            break
    charactersprovider.add_or_update_player(player)


def change_character_name(player_id, old_name, new_name):
    player: Player = charactersprovider.get_player(player_id)
    character = find_character_or_throw(player, old_name)
    character.character_name = new_name
    charactersprovider.add_or_update_player(player)


def swap_class_levels(player_id, character_name, class_to_remove_from, class_to_add_to):
    player = charactersprovider.get_player(player_id)
    character = find_character_or_throw(player, character_name)
    was_level_removed = False
    was_level_added = False
    for character_class in character.classes:
        if character_class.class_name == class_to_remove_from:
            if character_class.level <= 1:
                raise Exception("Class to remove from must be of level higher than 1.")
            else:
                character_class.level -= 1
                was_level_removed = True
        elif character_class.class_name == class_to_add_to:
            if character_class.level >= 20:
                raise Exception("Class to add to must be of level lower than 20.")
            else:
                character_class.level += 1
                was_level_added = True
    if not was_level_removed:
        raise Exception("Class to remove from was not found.")
    elif was_level_removed and not was_level_added:
        add_class_to_character_data(character, {class_to_add_to: 1}, False)
    charactersprovider.add_or_update_player(player)


def find_character_or_throw(player: Player, character_name) -> Character:
    for character in player.characters:
        if character.character_name == character_name:
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


# TODO: the below functions use "client" which is not correct. Functions that know about Discord should not be here.

async def refresh_player_message(client, player_id):
    await update_player_message(client, player_id, get_up_to_date_player_message(player_id))


async def update_player_message(client, player_id, new_message):
    players_channel = client.get_channel(channelsprovider.get_characters_info_channel_id())
    player_message_id = channelsprovider.get_player_message_id(player_id)
    try:
        player_message = await players_channel.fetch_message(player_message_id)
        await player_message.edit(content=new_message)
    except discord.NotFound:
        print(f'Message for player ID {player_id} was not found.')
