from source import itemssource
from model.rarity import rarity_strings_to_rarity
from source.sourcefields import *
from model.item import Item
from typing import Optional


cached_minor_items: Optional[list] = None


def get_all_items() -> list[Item]:
    return map_item_data_to_item_list(itemssource.get_all_items())


def get_all_major_items() -> list[Item]:
    return map_item_data_to_item_list(itemssource.get_all_major_items())


def get_all_minor_items() -> list[Item]:
    return map_item_data_to_item_list(get_all_minor_items_data())


def get_all_minor_items_data() -> list:
    global cached_minor_items
    if cached_minor_items is None:
        cached_minor_items = itemssource.get_all_minor_items()
    return cached_minor_items


def get_minor_item_by_name(item_name: str) -> Optional[Item]:
    all_items = get_all_minor_items_data()
    for item in all_items:
        if item[ITEM_FIELD_NAME] == item_name:
            return map_item_data_to_item(item)
    return None


def map_item_data_to_item_list(items_data: list) -> list[Item]:
    return list(map(lambda item: map_item_data_to_item(item), items_data))


def map_item_data_to_item(item) -> Item:
    return Item(
        name=item[ITEM_FIELD_NAME],
        description=item[ITEM_FIELD_DESCRIPTION],
        price=item[ITEM_FIELD_PRICE],
        rarity=rarity_strings_to_rarity(
            rarity=item[ITEM_FIELD_RARITY],
            rarity_level=item[ITEM_FIELD_RARITY_LEVEL]
        ),
        attunement=item[ITEM_FIELD_ATTUNEMENT],
        consumable=False if ITEM_FIELD_CONSUMABLE not in item else item[ITEM_FIELD_CONSUMABLE],
        official=False if ITEM_FIELD_OFFICIAL not in item else item[ITEM_FIELD_OFFICIAL],
        banned=False if ITEM_FIELD_BANNED not in item else item[ITEM_FIELD_BANNED]
    )
