from util import utils
from util.utils import *
from model.shopitem import ShopItem
from model.inventoryitem import InventoryItem
from model.item import Item


def get_inventory_item_row_string(magic_item: InventoryItem) -> str:
    magic_item_string = f'{magic_item.index}) **{magic_item.name}** - '
    item_quantity = magic_item.quantity
    if item_quantity != 1 and item_quantity != 0:
        magic_item_string += 'quantity: '
        quantity_string = str(item_quantity) if item_quantity != infinite_quantity else '*infinite*'
        magic_item_string += f'{quantity_string}, '
        magic_item_string += 'cost: '
    magic_item_string += f'{tokens_per_rarity(magic_item.rarity.rarity, magic_item.rarity.rarity_level)}\n'
    return magic_item_string


def get_sold_item_row_string(magic_item: ShopItem) -> str:
    magic_item_string = f'~~{magic_item.index}) {magic_item.name} - '
    item_quantity = magic_item.quantity
    if item_quantity != 1 and item_quantity != 0:
        magic_item_string += 'quantity: '
        quantity_string = str(item_quantity) if item_quantity != infinite_quantity else '*infinite*'
        magic_item_string += f'{quantity_string}, '
        magic_item_string += 'cost: '
    magic_item_string += f'{tokens_per_rarity(magic_item.rarity.rarity, magic_item.rarity.rarity_level)}~~ SOLD\n'
    return magic_item_string


def get_unsold_item_row_string_emoji(magic_item: ShopItem) -> str:
    emoji = utils.index_to_emoji(magic_item.index)
    magic_item_string = f'{magic_item.index} - {emoji}) **{magic_item.name}** - '
    magic_item_string += f'{tokens_per_rarity(magic_item.rarity.rarity, magic_item.rarity.rarity_level)}\n'
    return magic_item_string


def get_item_info_message(item: Item) -> str:
    item_info_string = f'**Name:** {item.name}\n' \
                       f'**Rarity:** {item.rarity.rarity}, {item.rarity.rarity_level}\n' \
                       f'**Requires attunement:** {"Yes" if item.attunement else "No"}\n'
    if item.official is not None and not item.official:
        item_info_string += f'**Homebrew:** {"No" if item.official else "Yes"}\n'
    item_info_string += f'**Description:** {item.description}\n'
    return item_info_string


def get_homebrew_item_confirmation_description(item: Item) -> str:
    return f'**Name:** {item.name}\n' \
                  f'**Rarity:** {item.rarity.rarity}, {item.rarity.rarity_level}\n' \
                  f'**Consumable:** {"Yes" if item.consumable else "No"}\n' \
                  f'**Requires attunement:** {"Yes" if item.attunement else "No"}\n' \
                  f'**Banned:** {"Yes" if item.banned else "No"}\n' \
                  f'**Description:** {item.description}'
