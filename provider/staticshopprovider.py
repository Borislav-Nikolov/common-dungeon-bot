from source import staticshopsource
from model.shopitem import ShopItem
from source.sourcefields import *
from model.rarity import rarity_strings_to_rarity


def add_or_update_in_static_shop(data: dict[int, ShopItem]):
    shop_data = dict()
    for key in data:
        item = data[key]
        shop_data[key] = {
                ITEM_FIELD_NAME: item.name,
                ITEM_FIELD_DESCRIPTION: item.description,
                ITEM_FIELD_PRICE: item.price,
                ITEM_FIELD_RARITY: item.rarity.rarity,
                ITEM_FIELD_RARITY_LEVEL: item.rarity.rarity_level,
                ITEM_FIELD_ATTUNEMENT: item.attunement,
                ITEM_FIELD_CONSUMABLE: item.consumable,
                ITEM_FIELD_OFFICIAL: item.official,
                ITEM_FIELD_BANNED: item.banned,
                INVENTORY_ITEM_FIELD_QUANTITY: item.quantity,
                INVENTORY_ITEM_FIELD_INDEX: item.index,
                SHOP_ITEM_FIELD_SOLD: item.sold
            }
    staticshopsource.update_in_static_shop(shop_data)


def get_static_shop_item(message_id: int) -> ShopItem:
    static_item = staticshopsource.get_static_shop_item(str(message_id))
    return ShopItem(
                name=static_item[ITEM_FIELD_NAME],
                description=static_item[ITEM_FIELD_DESCRIPTION],
                price=static_item[ITEM_FIELD_PRICE],
                rarity=rarity_strings_to_rarity(static_item[ITEM_FIELD_RARITY], static_item[ITEM_FIELD_RARITY_LEVEL]),
                attunement=static_item[ITEM_FIELD_ATTUNEMENT],
                consumable=False if ITEM_FIELD_CONSUMABLE not in static_item else static_item[ITEM_FIELD_CONSUMABLE],
                official=False if ITEM_FIELD_OFFICIAL not in static_item else static_item[ITEM_FIELD_OFFICIAL],
                banned=False if ITEM_FIELD_BANNED not in static_item else static_item[ITEM_FIELD_BANNED],
                quantity=static_item[INVENTORY_ITEM_FIELD_QUANTITY],
                index=static_item[INVENTORY_ITEM_FIELD_INDEX],
                sold=static_item[SHOP_ITEM_FIELD_SOLD]
            )
