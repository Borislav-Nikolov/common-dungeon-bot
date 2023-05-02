import utils
from characters import INVENTORY_ITEM_FIELD_QUANTITY
from utils import *

ITEM_FIELD_RARITY = "rarity"
ITEM_FIELD_NAME = "name"
ITEM_FIELD_PRICE = "price"
ITEM_FIELD_ATTUNEMENT = "attunement"
ITEM_FIELD_RARITY_LEVEL = "rarity_level"
ITEM_FIELD_DESCRIPTION = "description"
ITEM_FIELD_OFFICIAL = "official"
ITEM_FIELD_BANNED = "banned"
STRIKETHROUGH_AFFIX = "~~"


def get_sold_item_row_string(magic_item: dict) -> str:
    return STRIKETHROUGH_AFFIX + get_item_row_string(-1, magic_item) + STRIKETHROUGH_AFFIX


def get_item_row_string(index: int, magic_item: dict) -> str:
    letter_emoji = utils.index_to_emoji(index)
    tokens_num = f'**{tokens_per_rarity_number(magic_item[ITEM_FIELD_RARITY], magic_item[ITEM_FIELD_RARITY_LEVEL])}**'
    rarity_emoji = utils.get_rarity_emoji(magic_item[ITEM_FIELD_RARITY])
    item_name = magic_item[ITEM_FIELD_NAME]
    quantity = get_item_quantity_affix(magic_item[INVENTORY_ITEM_FIELD_QUANTITY])
    return f'{letter_emoji}    {tokens_num} {rarity_emoji}    {item_name} {quantity}\n'


def get_item_quantity_affix(quantity_number: int) -> str:
    if quantity_number == infinite_quantity:
        return '*(infinite)*'
    if quantity_number > 1:
        return f'**x{quantity_number}**'
    return ''
