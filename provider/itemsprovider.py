from source import itemssource
from model.rarity import rarity_strings_to_rarity
from source.sourcefields import *
from model.item import Item


def get_all_items() -> list[Item]:
    return map_item_data_to_item_list(itemssource.get_all_items())


def get_all_major_items() -> list[Item]:
    return map_item_data_to_item_list(itemssource.get_all_major_items())


def get_all_minor_items() -> list[Item]:
    return map_item_data_to_item_list(itemssource.get_all_minor_items())


def map_item_data_to_item_list(items_data: list) -> list[Item]:
    items: list[Item] = list()
    for item in items_data:
        items.append(
            Item(
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
        )
    return items


def update_in_items(item_data):
    return itemssource.update_in_items(item_data)
