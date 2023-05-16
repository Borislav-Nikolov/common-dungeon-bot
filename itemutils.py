import utils
from utils import *

ITEM_FIELD_RARITY = "rarity"
ITEM_FIELD_NAME = "name"
ITEM_FIELD_PRICE = "price"
ITEM_FIELD_ATTUNEMENT = "attunement"
ITEM_FIELD_RARITY_LEVEL = "rarity_level"
ITEM_FIELD_DESCRIPTION = "description"
ITEM_FIELD_OFFICIAL = "official"
ITEM_FIELD_BANNED = "banned"


def get_unsold_item_row_string(
        index: int,
        magic_item: dict,
        field_key_quantity: str
) -> str:
    magic_item_string = f'{index}) **{magic_item[ITEM_FIELD_NAME]}** - '
    item_quantity = magic_item[field_key_quantity]
    if item_quantity != 1 and item_quantity != 0:
        magic_item_string += 'quantity: '
        quantity_string = str(item_quantity) if item_quantity != infinite_quantity else '*infinite*'
        magic_item_string += f'{quantity_string}, '
        magic_item_string += 'cost: '
    magic_item_string += f'{tokens_per_rarity(magic_item[ITEM_FIELD_RARITY], magic_item[ITEM_FIELD_RARITY_LEVEL])}\n'
    return magic_item_string


def get_sold_item_row_string(
        index: int,
        magic_item: dict,
        field_key_quantity: str
) -> str:
    magic_item_string = f'~~{index}) {magic_item[ITEM_FIELD_NAME]} - '
    item_quantity = magic_item[field_key_quantity]
    if item_quantity != 1 and item_quantity != 0:
        magic_item_string += 'quantity: '
        quantity_string = str(item_quantity) if item_quantity != infinite_quantity else '*infinite*'
        magic_item_string += f'{quantity_string}, '
        magic_item_string += 'cost: '
    magic_item_string += f'{tokens_per_rarity(magic_item[ITEM_FIELD_RARITY], magic_item[ITEM_FIELD_RARITY_LEVEL])}~~ SOLD\n'
    return magic_item_string


def get_unsold_item_row_string_emoji(
        index: int,
        magic_item: dict,
        field_key_quantity: str
) -> str:
    emoji = utils.index_to_emoji(index)
    magic_item_string = f'{index} - {emoji}) **{magic_item[ITEM_FIELD_NAME]}** - '
    item_quantity = magic_item[field_key_quantity]
    if item_quantity != 1 and item_quantity != 0:
        magic_item_string += 'quantity: '
        quantity_string = str(item_quantity) if item_quantity != infinite_quantity else '*infinite*'
        magic_item_string += f'{quantity_string}, '
        magic_item_string += 'cost: '
    magic_item_string += f'{tokens_per_rarity(magic_item[ITEM_FIELD_RARITY], magic_item[ITEM_FIELD_RARITY_LEVEL])}\n'
    return magic_item_string


def get_item_info_message(item: dict) -> str:
    item_info_string = f'**Name:** {item[ITEM_FIELD_NAME]}\n'
    item_info_string += f'**Rarity:** {item[ITEM_FIELD_RARITY]}, {item[ITEM_FIELD_RARITY_LEVEL]}\n'
    item_info_string += f'**Requires attunement:** {"Yes" if item[ITEM_FIELD_ATTUNEMENT] else "No"}\n'
    item_info_string += f'**Homebrew:** {"No" if item[ITEM_FIELD_OFFICIAL] else "Yes"}\n'
    item_info_string += f'**Description:** {item[ITEM_FIELD_DESCRIPTION]}\n'
    return item_info_string
