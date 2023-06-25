from __future__ import print_function

import characters
import firebase
import random
import copy

import itemutils
from itemutils import *

SHOP_ITEM_FIELD_QUANTITY = "quantity"
SHOP_ITEM_FIELD_SOLD = "sold"
SHOP_ITEM_FIELD_INDEX = "index"

# number restricted because of emoji limit
SHOP_MAX_NUMBER_OF_ITEMS = 20


def generate_new_magic_shop(character_levels_csv: str) -> str:
    magic_shop_list = generate_random_shop_list(character_levels_csv)
    magic_shop_string = ''
    counter = 1
    for magic_item in magic_shop_list:
        if not(SHOP_ITEM_FIELD_QUANTITY in magic_item):
            magic_item[SHOP_ITEM_FIELD_QUANTITY] = 1
        magic_item[SHOP_ITEM_FIELD_SOLD] = False
        magic_item[SHOP_ITEM_FIELD_INDEX] = counter
        magic_shop_string += get_unsold_item_row_string_emoji(counter, magic_item, SHOP_ITEM_FIELD_QUANTITY)
        counter += 1
    firebase.set_in_magic_shop(magic_shop_list)
    return magic_shop_string


def generate_random_shop_list(character_levels_csv: str) -> list:
    character_levels_list: list = split_strip(character_levels_csv, ',')
    if len(character_levels_list) >= SHOP_MAX_NUMBER_OF_ITEMS:
        raise Exception("Too many character levels. Can't generate that many items.")
    character_rarity_ordinal_list = list(map(lambda it: level_to_rarity_ordinal(int(it)), character_levels_list))
    character_rarity_ordinal_list.sort(reverse=True)
    max_rarity_ordinal = max(character_rarity_ordinal_list)
    items_from_firebase = firebase.get_all_items_from_firebase()
    filtered_items = list()
    common = list()
    uncommon = list()
    rare = list()
    very_rare = list()
    legendary = list()
    potion_of_healing = dict()
    for item in items_from_firebase:
        rarity = item[ITEM_FIELD_RARITY].lower()
        if rarity == COMMON and max_rarity_ordinal >= COMMON_ORDINAL:
            common.append(item)
            # add only potion of healing for now
            if item[ITEM_FIELD_NAME] == "Potion of Healing":
                item[SHOP_ITEM_FIELD_QUANTITY] = infinite_quantity
                potion_of_healing = item
        elif rarity == UNCOMMON and max_rarity_ordinal >= UNCOMMON_ORDINAL:
            uncommon.append(item)
            filtered_items.append(item)
        elif rarity == RARE and max_rarity_ordinal >= RARE_ORDINAL:
            rare.append(item)
            filtered_items.append(item)
        elif rarity == VERY_RARE and max_rarity_ordinal >= VERY_RARE_ORDINAL:
            very_rare.append(item)
            filtered_items.append(item)
        elif rarity == LEGENDARY and max_rarity_ordinal >= LEGENDARY_ORDINAL:
            legendary.append(item)
            filtered_items.append(item)
    magic_shop_list = list()
    for character_rarity_ordinal in character_rarity_ordinal_list:
        if character_rarity_ordinal == COMMON_ORDINAL:
            common_item_clone = copy.deepcopy(random.choice(common))
            magic_shop_list.append(common_item_clone)
        elif character_rarity_ordinal == UNCOMMON_ORDINAL:
            uncommon_item_clone = copy.deepcopy(random.choice(uncommon))
            magic_shop_list.append(uncommon_item_clone)
        elif character_rarity_ordinal == RARE_ORDINAL:
            rare_item_clone = copy.deepcopy(random.choice(rare))
            magic_shop_list.append(rare_item_clone)
        elif character_rarity_ordinal == VERY_RARE_ORDINAL:
            very_rare_item_clone = copy.deepcopy(random.choice(very_rare))
            magic_shop_list.append(very_rare_item_clone)
        elif character_rarity_ordinal == LEGENDARY_ORDINAL:
            legendary_item_clone = copy.deepcopy(random.choice(legendary))
            magic_shop_list.append(legendary_item_clone)

    remaining_number = (SHOP_MAX_NUMBER_OF_ITEMS - 1) - len(magic_shop_list)
    if remaining_number > 0:
        rest_items = random.sample(filtered_items, remaining_number)
        for item in rest_items:
            magic_shop_list.append(item)
    magic_shop_list.append(potion_of_healing)
    return magic_shop_list


def get_current_shop_string() -> str:
    items = firebase.get_magic_shop_items()
    final_string = ''
    for item in items:
        if item[SHOP_ITEM_FIELD_SOLD] is False:
            final_string += get_unsold_item_row_string_emoji(item[SHOP_ITEM_FIELD_INDEX], item, SHOP_ITEM_FIELD_QUANTITY)
        else:
            final_string += get_sold_item_row_string(item[SHOP_ITEM_FIELD_INDEX], item, SHOP_ITEM_FIELD_QUANTITY)
    return final_string


def sell_item(player_id, item_index) -> str:
    items = firebase.get_magic_shop_items()
    sold_item_name = ''
    sold = False
    for item in items:
        if item[SHOP_ITEM_FIELD_INDEX] == item_index and item[SHOP_ITEM_FIELD_SOLD] is False:
            if item[SHOP_ITEM_FIELD_QUANTITY] != infinite_quantity:
                item[SHOP_ITEM_FIELD_QUANTITY] = item[SHOP_ITEM_FIELD_QUANTITY] - 1
                quantity = item[SHOP_ITEM_FIELD_QUANTITY]
                if quantity < 0:
                    raise Exception("Item quantity reached.")
                if quantity == 0:
                    item[SHOP_ITEM_FIELD_SOLD] = True
            if characters.subtract_player_tokens_for_rarity(
                    player_id,
                    item[ITEM_FIELD_RARITY],
                    item[ITEM_FIELD_RARITY_LEVEL]):
                item_name_lower = item[ITEM_FIELD_NAME].lower()
                is_consumable = False if item[ITEM_FIELD_CONSUMABLE] is None else item[ITEM_FIELD_CONSUMABLE]
                is_probably_consumable = "potion" not in item_name_lower and "scroll" not in item_name_lower\
                                         and "ammunition" not in item_name_lower
                if is_consumable or is_probably_consumable:
                    item_copy = copy.deepcopy(item)
                    del item_copy[SHOP_ITEM_FIELD_QUANTITY]
                    del item_copy[SHOP_ITEM_FIELD_INDEX]
                    del item_copy[SHOP_ITEM_FIELD_SOLD]
                    characters.add_item_to_inventory(player_id, item_copy)
                sold_item_name = item[ITEM_FIELD_NAME]
                sold = True
    if sold:
        firebase.set_in_magic_shop(items)
    return sold_item_name


def get_item_name_by_index(index: int) -> str:
    items = firebase.get_magic_shop_items()
    for item in items:
        if item[SHOP_ITEM_FIELD_INDEX] == index and not item[SHOP_ITEM_FIELD_SOLD]:
            return item[ITEM_FIELD_NAME]


def get_shop_item_description(item_index) -> list:
    items = firebase.get_magic_shop_items()
    for item in items:
        if item[SHOP_ITEM_FIELD_INDEX] == int(item_index) and ITEM_FIELD_DESCRIPTION in item:
            return split_by_number_of_characters(itemutils.get_item_info_message(item), 2000)
    return ["*couldn't find item description*"]


def refund_item_by_index(player_id, item_index: int) -> str:
    item = characters.get_item_from_inventory(player_id, item_index)
    refunded = characters.subtract_item_from_inventory(player_id, item)
    if refunded:
        return item[ITEM_FIELD_NAME]
    return ""


def refund_item(player_id, item_rarity, item_rarity_level) -> bool:
    return characters.add_player_tokens_for_rarity(player_id, item_rarity, item_rarity_level)


def get_sold_item_string(player_id, item_name) -> str:
    return f'<@{player_id}> bought {item_name}.'


def get_failed_to_buy_item_string(player_id, item_name) -> str:
    return f'<@{player_id}> transaction for {item_name} failed.'


def get_refunded_item_string(player_id, item_name) -> str:
    return f'<@{player_id}> sold {item_name}.'
