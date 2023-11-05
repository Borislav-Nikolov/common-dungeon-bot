from model.shopitem import ShopItem
from source.sourcefields import *
from model.rarity import rarity_strings_to_rarity
from source import magicshopsource, channelssource


def get_shop_channel_id() -> int:
    return channelssource.get_shop_channel_id()


def get_shop_message_id() -> int:
    return channelssource.get_shop_message_id()


def set_in_magic_shop(items: list[ShopItem]):
    items_data = list()
    for item in items:
        items_data.append(
            {
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
        )
    magicshopsource.set_in_magic_shop(items_data)


def get_magic_shop_items() -> list[ShopItem]:
    shop_items_data = magicshopsource.get_magic_shop_items()
    shop_items = list[ShopItem]()
    for source_item in shop_items_data:
        shop_items.append(
            ShopItem(
                name=source_item[ITEM_FIELD_NAME],
                description=source_item[ITEM_FIELD_DESCRIPTION],
                price=source_item[ITEM_FIELD_PRICE],
                rarity=rarity_strings_to_rarity(source_item[ITEM_FIELD_RARITY], source_item[ITEM_FIELD_RARITY_LEVEL]),
                attunement=source_item[ITEM_FIELD_ATTUNEMENT],
                consumable=False if ITEM_FIELD_CONSUMABLE not in source_item else source_item[ITEM_FIELD_CONSUMABLE],
                official=False if ITEM_FIELD_OFFICIAL not in source_item else source_item[ITEM_FIELD_OFFICIAL],
                banned=False if ITEM_FIELD_BANNED not in source_item else source_item[ITEM_FIELD_BANNED],
                quantity=source_item[INVENTORY_ITEM_FIELD_QUANTITY],
                index=source_item[INVENTORY_ITEM_FIELD_INDEX],
                sold=source_item[SHOP_ITEM_FIELD_SOLD]
            )
        )
    return shop_items
