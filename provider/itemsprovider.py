from source import itemssource
from model.rarity import rarity_strings_to_rarity
from provider.sourcefields import *
from model.item import Item


def get_all_items() -> list[Item]:
    items: list[Item] = list()
    items_data: dict = itemssource.get_all_items()
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
                consumable=item[ITEM_FIELD_CONSUMABLE],
                official=item[ITEM_FIELD_OFFICIAL],
                banned=item[ITEM_FIELD_BANNED]
            )
        )
    return items


def update_in_items(item_data):
    return itemssource.update_in_items(item_data)
