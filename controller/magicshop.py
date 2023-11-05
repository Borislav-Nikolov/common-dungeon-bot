from __future__ import print_function

from controller import characters
from provider import magicshopprovider, itemsprovider
import random

from util import itemutils
from util.itemutils import *

# number restricted because of emoji limit
SHOP_MAX_NUMBER_OF_ITEMS = 20


def generate_new_magic_shop(character_levels_csv: str) -> str:
    magic_shop_list: list[Item] = generate_random_shop_list(character_levels_csv)
    shop_items: list[ShopItem] = list()
    magic_shop_string = ''
    counter = 1
    for magic_item in magic_shop_list:
        new_shop_item = ShopItem(
            name=magic_item.name,
            description=magic_item.description,
            price=magic_item.price,
            rarity=magic_item.rarity,
            attunement=magic_item.attunement,
            consumable=magic_item.consumable,
            official=magic_item.official,
            banned=magic_item.banned,
            quantity=infinite_quantity,
            index=counter,
            sold=False
        )
        shop_items.append(new_shop_item)
        magic_shop_string += get_unsold_item_row_string_emoji(new_shop_item)
        counter += 1
    magicshopprovider.set_in_magic_shop(shop_items)
    return magic_shop_string


def generate_random_shop_list(character_levels_csv: str) -> list[Item]:
    character_levels_list: list = split_strip(character_levels_csv, ',')
    if len(character_levels_list) >= SHOP_MAX_NUMBER_OF_ITEMS:
        raise Exception("Too many character levels. Can't generate that many items.")
    character_rarity_ordinal_list = list(map(lambda it: level_to_rarity_ordinal(int(it)), character_levels_list))
    character_rarity_ordinal_list.sort(reverse=True)
    max_rarity_ordinal = max(character_rarity_ordinal_list)
    items_from_firebase: list[Item] = itemsprovider.get_all_major_items()
    filtered_items = list()
    common = list()
    uncommon = list()
    rare = list()
    very_rare = list()
    legendary = list()
    for item in items_from_firebase:
        rarity = item.rarity
        if rarity.rarity == COMMON and max_rarity_ordinal >= COMMON_ORDINAL:
            common.append(item)
        elif rarity.rarity == UNCOMMON and max_rarity_ordinal >= UNCOMMON_ORDINAL:
            uncommon.append(item)
            filtered_items.append(item)
        elif rarity.rarity == RARE and max_rarity_ordinal >= RARE_ORDINAL:
            rare.append(item)
            filtered_items.append(item)
        elif rarity.rarity == VERY_RARE and max_rarity_ordinal >= VERY_RARE_ORDINAL:
            very_rare.append(item)
            filtered_items.append(item)
        elif rarity.rarity == LEGENDARY and max_rarity_ordinal >= LEGENDARY_ORDINAL:
            legendary.append(item)
            filtered_items.append(item)
    magic_shop_list = list()
    for character_rarity_ordinal in character_rarity_ordinal_list:
        if character_rarity_ordinal == COMMON_ORDINAL:
            common_item_clone = copy.deepcopy(random.choice(common))
            approved = False
            # while not approved:
            #     for magic_item in magic_shop_list:
                    
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

    remaining_number = SHOP_MAX_NUMBER_OF_ITEMS - len(magic_shop_list)
    if remaining_number > 0:
        rest_items = random.sample(filtered_items, remaining_number)
        for item in rest_items:
            magic_shop_list.append(item)
    counter = 1
    for item in magic_shop_list:
        print(f'{counter}) {item}')
        counter = counter + 1
    return magic_shop_list


def get_current_shop_string() -> str:
    items: list[ShopItem] = magicshopprovider.get_magic_shop_items()
    final_string = ''
    for item in items:
        if item.sold is False:
            final_string += get_unsold_item_row_string_emoji(item)
        else:
            final_string += get_sold_item_row_string(item)
    return final_string


def sell_item(player_id, item_index) -> str:
    items: list[ShopItem] = magicshopprovider.get_magic_shop_items()
    sold_item_name = ''
    sold = False
    for item in items:
        if item.index == item_index and item.sold is False:
            if item.quantity != infinite_quantity:
                item.quantity = item.quantity - 1
                quantity = item.quantity
                if quantity < 0:
                    raise Exception("Item already sold.")
                if quantity == 0:
                    item.sold = True
            if characters.subtract_player_tokens_for_rarity(player_id, item.rarity.rarity, item.rarity.rarity_level):
                item_name_lower = item.name.lower()
                is_probably_consumable = "potion" not in item_name_lower and "scroll" not in item_name_lower\
                                         and "ammunition" not in item_name_lower
                if item.consumable or is_probably_consumable:
                    characters.add_single_quantity_item_to_inventory(player_id, copy.deepcopy(item))
                sold_item_name = item.name
                sold = True
    if sold:
        magicshopprovider.set_in_magic_shop(items)
    return sold_item_name


def get_item_name_by_index(index: int) -> str:
    items = magicshopprovider.get_magic_shop_items()
    for item in items:
        if item.index == index and not item.sold:
            return item.name


def get_shop_item_description(item_index) -> list:
    items = magicshopprovider.get_magic_shop_items()
    for item in items:
        if item.index == int(item_index):
            return split_by_number_of_characters(itemutils.get_item_info_message(item), 2000)
    return ["*couldn't find item description*"]


def refund_item(player_id, item_rarity, item_rarity_level) -> bool:
    return characters.add_player_tokens_for_rarity(player_id, item_rarity, item_rarity_level)


def get_sold_item_string(player_id, item_name) -> str:
    return f'<@{player_id}> bought {item_name}.'


def get_failed_to_buy_item_string(player_id, item_name) -> str:
    return f'<@{player_id}> transaction for {item_name} failed.'


def get_refunded_item_string(player_id, item_name) -> str:
    return f'<@{player_id}> sold {item_name}.'
