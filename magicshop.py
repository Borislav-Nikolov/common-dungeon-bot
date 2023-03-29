from __future__ import print_function

import characters
import firebase
import random
import copy

from itemutils import *

SHOP_ITEM_FIELD_QUANTITY = "quantity"
SHOP_ITEM_FIELD_SOLD = "sold"
SHOP_ITEM_FIELD_INDEX = "index"


def generate_new_magic_shop(character_levels_csv: str) -> str:
    magic_shop_list = generate_random_shop_list(character_levels_csv)
    magic_shop_string = ''
    counter = 1
    for magic_item in magic_shop_list:
        if not(SHOP_ITEM_FIELD_QUANTITY in magic_item):
            magic_item[SHOP_ITEM_FIELD_QUANTITY] = 1
        magic_item[SHOP_ITEM_FIELD_SOLD] = False
        magic_item[SHOP_ITEM_FIELD_INDEX] = counter
        magic_shop_string += get_unsold_item_row_string(counter, magic_item, SHOP_ITEM_FIELD_QUANTITY)
        counter += 1
    firebase.set_in_magic_shop(magic_shop_list)
    return magic_shop_string


def generate_random_shop_list(character_levels_csv: str) -> list:
    character_levels_list: list = split_strip(character_levels_csv, ',')
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

    rest_items = random.sample(filtered_items, 16)
    for item in rest_items:
        magic_shop_list.append(item)
    magic_shop_list.append(potion_of_healing)
    return magic_shop_list


def get_current_shop_string() -> str:
    items = firebase.get_magic_shop_items()
    final_string = ''
    for item in items:
        if item[SHOP_ITEM_FIELD_SOLD] is False:
            final_string += get_unsold_item_row_string(item[SHOP_ITEM_FIELD_INDEX], item, SHOP_ITEM_FIELD_QUANTITY)
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


def get_shop_item_description(item_index) -> str:
    items = firebase.get_magic_shop_items()
    for item in items:
        if item[SHOP_ITEM_FIELD_INDEX] == int(item_index) and ITEM_FIELD_DESCRIPTION in item:
            return item[ITEM_FIELD_DESCRIPTION]
    return "*couldn't find item description*"


def refund_item(player_id, item_rarity, item_rarity_level) -> bool:
    return characters.add_player_tokens_for_rarity(player_id, item_rarity, item_rarity_level)


def get_sold_item_string(player_id, item_name) -> str:
    return f'<@{player_id}> bought {item_name}.'
