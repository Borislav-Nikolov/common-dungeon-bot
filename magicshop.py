from __future__ import print_function

import os.path
import firebase
import random

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

COMMON = "common"
COMMON_ORDINAL = 1
UNCOMMON = "uncommon"
UNCOMMON_ORDINAL = 2
RARE = "rare"
RARE_ORDINAL = 3
VERY_RARE = "very rare"
VERY_RARE_ORDINAL = 4
LEGENDARY = "legendary"
LEGENDARY_ORDINAL = 5
TYPE_MINOR = "minor"
TYPE_MAJOR = "major"

infinite_quantity = -1


def __rarity_to_ordinal(rarity) -> int:
    rarity = rarity.lower()
    if rarity == COMMON:
        return COMMON_ORDINAL
    if rarity == UNCOMMON:
        return UNCOMMON_ORDINAL
    if rarity == RARE:
        return RARE_ORDINAL
    if rarity == VERY_RARE:
        return VERY_RARE_ORDINAL
    if rarity == LEGENDARY:
        return LEGENDARY_ORDINAL


def generate_new_magic_shop(max_rarity) -> str:
    max_rarity_ordinal = __rarity_to_ordinal(max_rarity)
    items_from_firebase = firebase.get_all_items_from_firebase()
    common = list()
    uncommon = list()
    rare = list()
    very_rare = list()
    legendary = list()
    for item in items_from_firebase:
        rarity = item["rarity"].lower()
        if rarity == COMMON and max_rarity_ordinal >= COMMON_ORDINAL:
            common.append(item)
        if rarity == UNCOMMON and max_rarity_ordinal >= UNCOMMON_ORDINAL:
            uncommon.append(item)
        if rarity == RARE and max_rarity_ordinal >= RARE_ORDINAL:
            rare.append(item)
        if rarity == VERY_RARE and max_rarity_ordinal >= VERY_RARE_ORDINAL:
            very_rare.append(item)
        if rarity == LEGENDARY and max_rarity_ordinal >= LEGENDARY_ORDINAL:
            legendary.append(item)
    random.shuffle(common)
    random.shuffle(uncommon)
    random.shuffle(rare)
    random.shuffle(very_rare)
    random.shuffle(legendary)
    magic_shop_list = list()
    for legendary_item in legendary[0:1]:
        if random.randint(1, 6) == 6:
            magic_shop_list.append(legendary_item)
    for very_rare_item in very_rare[0:2]:
        if random.randint(1, 3) == 3:
            magic_shop_list.append(very_rare_item)
    for rare_item in rare[0:3]:
        if random.randint(1, 2) == 2:
            magic_shop_list.append(rare_item)
    magic_shop_size = 16
    remaining_items = magic_shop_size - len(magic_shop_list)
    for uncommon_item in uncommon[0:remaining_items]:
        magic_shop_list.append(uncommon_item)
    magic_shop_list.reverse()
    for common_item in common:
        magic_shop_list.append(common_item)
    potion_item = {
        "name": "Potion of healing 2d4+2 (infinite amount)",
        "price": "50 gp",
        "rarity": "Common",
        "attunement": "NO",
        "rarity_level": "MINOR",
        "quantity": infinite_quantity
    }
    magic_shop_list.append(potion_item)
    magic_shop_string = ''
    counter = 1
    for magic_item in magic_shop_list:
        if not("quantity" in magic_item):
            magic_item["quantity"] = 1
        magic_item["sold"] = False
        magic_item["index"] = counter
        magic_shop_string += \
            f'{counter}) **{magic_item["name"]}** - {tokens_per_rarity(magic_item["rarity"], magic_item["rarity_level"])}\n'
        counter += 1
    firebase.set_in_magic_shop(magic_shop_list)
    return magic_shop_string


def get_current_shop_string(items) -> str:
    final_string = ''
    for item in items:
        if item["sold"] is False:
            final_string += f'{item["index"]}) **{item["name"]}** - {tokens_per_rarity(item["rarity"], item["rarity_level"])}\n'
        else:
            final_string += f'~~{item["index"]}) **{item["name"]}** - {tokens_per_rarity(item["rarity"], item["rarity_level"])}~~ SOLD\n'
    return final_string


def sell_item(index) -> str:
    items = firebase.get_magic_shop_items()
    sold = False
    for item in items:
        if item["quantity"] != infinite_quantity and item["index"] == index and item["sold"] is False:
            item["quantity"] = item["quantity"] - 1
            quantity = item["quantity"]
            if quantity < 0:
                raise Exception("Item quantity reached.")
            if quantity == 0:
                sold = True
                item["sold"] = True
    if sold:
        firebase.set_in_magic_shop(items)
        return get_current_shop_string(items)
    else:
        return ""


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

spreadsheet = '1nnB8VmIUtkYCIQXcaQIsEHj10K7OkELYRloSJmbK-Ow'
randomized_item_list_spreadsheet_range = 'Magic Shop'
full_item_list_spreadsheet_range = 'Magic Items'


def get_item_names_from_spreadsheet() -> str:
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet,
                                    range=randomized_item_list_spreadsheet_range).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return ''

        values.pop(0)
        item_names = ""
        for row in values:
            print(row)
            token_cost = '1 common token' if len(row) < 3 else tokens_per_rarity(row[2], row[4])
            name = str(f'**{row[1]}** - {token_cost}\n')
            item_names += name

        return item_names
    except HttpError as err:
        print(err)


def write_items(values):
    with open('items.json', 'w') as items:
        items.write('[')
        for row in values:
            print(len(row))
            if len(row) > 3:
                items.write('{')
                items.write(
                    f'"name":"{row[0]}","price":"{row[1]}","rarity":"{row[2]}","attunement":"{row[3]}","rarity_level":"{row[5]}"')
                items.write('},')

        items.write(']')


def tokens_per_rarity(rarity, rarity_type) -> str:
    rarity = rarity.lower()
    rarity_type = rarity_type.lower()
    if rarity == COMMON:
        return '1 common token'
    elif rarity == UNCOMMON and rarity_type == TYPE_MINOR:
        return '3 uncommon tokens'
    elif rarity == UNCOMMON and rarity_type == TYPE_MAJOR:
        return '6 uncommon tokens'
    elif rarity == RARE and rarity_type == TYPE_MINOR:
        return '4 rare tokens'
    elif rarity == RARE and rarity_type == TYPE_MAJOR:
        return '8 rare tokens'
    elif rarity == VERY_RARE and rarity_type == TYPE_MINOR:
        return '5 very rare tokens'
    elif rarity == VERY_RARE and rarity_type == TYPE_MAJOR:
        return '10 very rare tokens'
    elif rarity == LEGENDARY and rarity_type == TYPE_MINOR:
        return '5 legendary tokens'
    elif rarity == LEGENDARY and rarity_type == TYPE_MAJOR:
        return '10 legendary tokens'
