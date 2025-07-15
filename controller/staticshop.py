import copy

from model.item import Item
from model.shopitem import ShopItem
from util import utils
from controller import characters


def item_to_shop_item(item: Item) -> ShopItem:
    return ShopItem(
            name=item.name,
            description=item.description,
            price=item.price,
            rarity=item.rarity,
            attunement=item.attunement,
            consumable=item.consumable,
            official=item.official,
            banned=item.banned,
            always_available=item.always_available,
            quantity=utils.infinite_quantity,
            index=0,
            sold=False,
            sellable=True
    )


def sell_item(player_id, item: ShopItem) -> bool:
    if characters.subtract_player_tokens_for_rarity(player_id, item.rarity.rarity, item.rarity.rarity_level):
        item_name_lower = item.name.lower()
        is_probably_not_consumable = "potion" not in item_name_lower and "scroll" not in item_name_lower \
                                     and "ammunition" not in item_name_lower

        if not item.consumable and is_probably_not_consumable:
            characters.add_single_quantity_item_to_inventory(player_id, copy.deepcopy(item))
        return True
    return False

