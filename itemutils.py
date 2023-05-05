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
STRIKETHROUGH_AFFIX = "~~"


def get_sold_item_row_string(magic_item: dict) -> str:
    return STRIKETHROUGH_AFFIX + get_item_row_string(magic_item, index=-1, quantity=0) + STRIKETHROUGH_AFFIX


def get_item_row_string(magic_item: dict, index: int, quantity: int) -> str:
    letter_emoji = utils.index_to_emoji(index)
    price = get_price(magic_item)
    rarity_emoji = utils.get_rarity_emoji(magic_item[ITEM_FIELD_RARITY])
    item_name = magic_item[ITEM_FIELD_NAME]
    quantity = get_item_quantity_affix(quantity)
    return f'{letter_emoji}\t{price} {rarity_emoji}\t{item_name} {quantity}\n'


def get_item_quantity_affix(quantity_number: int) -> str:
    if quantity_number == infinite_quantity:
        return '*(infinite)*'
    if quantity_number > 1:
        return f'**x{quantity_number}**'
    return ''


# This adds two spaces before the price if it is a single digit number so the text can be aligned vertically.
def get_price(magic_item: dict) -> str:
    price_number = tokens_per_rarity_number(magic_item[ITEM_FIELD_RARITY], magic_item[ITEM_FIELD_RARITY_LEVEL])
    price_string = f'**{price_number}**'
    if price_number < 10:
        price_string = f'  {price_string}'
    return price_string
