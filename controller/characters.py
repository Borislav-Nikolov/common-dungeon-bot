from provider import charactersprovider
from util.itemutils import *
from model.player import Player
from model.character import Character
from model.inventoryitem import InventoryItem
from model.characterclass import CharacterClass
from model.inventorymessage import InventoryMessage
from model.reserveditemmessage import ReservedItemMessage
from model.rarity import rarity_strings_to_rarity
from model.playerrole import PlayerRole
from typing import Optional
from util import charactersutils


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
    inventory_string = f'# Inventory\n' \
                       f'{tokens_string(player)}\n\n'
    count = 0
    count_to_string = list()
    for item in inventory:
        count += 1
        inventory_string += get_inventory_item_row_string(magic_item=item)
        if count % 20 == 0 or count == len(inventory):
            count_to_string.append({20 if count % 20 == 0 else count % 20: inventory_string})
            inventory_string = ""
    return count_to_string


def get_reserved_item_string(player_id) -> Optional[str]:
    item_string: Optional[str] = None
    player = charactersprovider.get_player(player_id)
    item = player.reserved_items[0] if len(player.reserved_items) > 0 else None
    if item:
        item_string = get_reserved_item_message(item)
    return item_string


def set_inventory_messages(player_id, inventory_messages: list[InventoryMessage]):
    player = charactersprovider.get_player(player_id)
    player.inventory_messages = inventory_messages
    charactersprovider.add_or_update_player(player)


def set_reserved_item_message(player_id, reserved_item_message_id):
    player = charactersprovider.get_player(player_id)
    player.reserved_items_messages = [ReservedItemMessage(beginning_index=1, message_id=reserved_item_message_id)]
    charactersprovider.add_or_update_player(player)


def remove_reserved_item_and_message(player_id):
    player = charactersprovider.get_player(player_id)
    player.reserved_items = list()
    player.reserved_items_messages = list()
    charactersprovider.add_or_update_player(player)


def get_inventory_messages(player_id) -> list[InventoryMessage]:
    return charactersprovider.get_player(player_id).inventory_messages


def get_reserved_items_messages(player_id) -> list[ReservedItemMessage]:
    return charactersprovider.get_player(player_id).reserved_items_messages


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


def get_detailed_player_message(player_id) -> str:
    player: Player = charactersprovider.get_player(player_id)
    level = player.player_level
    player_string = f'# Player: {player.name}\n' \
                    f'**Player level:** {level} - {player.sessions_on_this_level}/6 to level {level + 1}\n' \
                    f'{tokens_string(player)}'
    characters_string = '\n**Characters:**\n'
    for character in player.characters:
        characters_string += f'{charactersutils.status_emoji(character.status)} ' \
                             f'{get_character_row_string(character, detailed=True)}\n'
    return f'{player_string}{characters_string}'


def tokens_string(player: Player) -> str:
    return f'**Tokens:** {player.common_tokens} common, ' \
           f'{player.uncommon_tokens} uncommon, ' \
           f'{player.rare_tokens} rare, ' \
           f'{player.very_rare_tokens} very rare, ' \
           f'{player.legendary_tokens} legendary'


def get_up_to_date_player_message(player_id) -> str:
    player: Player = charactersprovider.get_player(player_id)
    level = player.player_level
    player_string = f'# Player: {player.name} <@{player.player_id}>\n' \
                    f'**Player level:** {level} - {player.sessions_on_this_level}/6 to level {level + 1}\n'
    characters_string = '\n**Characters:**\n'
    hidden_characters_count = 0
    for character in player.characters:
        if character.status == charactersutils.CHARACTER_STATUS_ACTIVE:
            characters_string += f'* {get_character_row_string(character, detailed=False)}\n'
        else:
            hidden_characters_count += 1
    if hidden_characters_count > 0:
        string_based_on_number = 'character is' if hidden_characters_count == 1 else 'characters are'
        characters_string += f'*({hidden_characters_count} {string_based_on_number} hidden)*'
    return f'{player_string}{characters_string}'


def get_character_row_string(character: Character, detailed: bool) -> str:
    character_string = f'{character.character_name} (level **{character.character_level}**) - '
    class_index = 0
    for character_class in character.classes:
        character_string += f'{character_class.class_name} {character_class.level}'
        if class_index != len(character.classes) - 1:
            character_string += ' - '
        class_index += 1
    if character.character_level < 20:
        character_level = character.character_level
        current_sessions = character.sessions_on_this_level
        games_to_next_level = utils.sessions_to_next_level(character_level) - current_sessions
        game_word = 'game' if games_to_next_level == 1 else 'games'
        character_string += f' - {games_to_next_level} {game_word} to next level'
    if detailed:
        character_string += f' - Last DM: {character.last_dm}'
    return character_string


def find_character_or_throw(player: Player, character_name) -> Character:
    for character in player.characters:
        if character.character_name == character_name:
            return character
    raise ValueError("Character not found.")


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


def get_player_reserved_item(player_id) -> Optional[Item]:
    player = charactersprovider.get_player(player_id)
    if len(player.reserved_items) > 0:
        return player.reserved_items[0]
    else:
        return None


def set_reserved_item(player_id, item: Item) -> bool:
    item_copy = copy.deepcopy(item)
    player = charactersprovider.get_player(player_id)
    player.reserved_items = [item_copy]
    charactersprovider.add_or_update_player(player)
    return True


def change_player_id(old_id, new_id):
    old_id_str = str(old_id)
    new_id_str = str(new_id)
    player_data = charactersprovider.get_player(old_id_str)
    player_data.player_id = new_id_str
    charactersprovider.add_or_update_player(player_data)
    charactersprovider.delete_player(old_id_str)


def is_admin(player_id) -> bool:
    return charactersprovider.get_player(player_id).player_role == PlayerRole.Admin
