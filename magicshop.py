from __future__ import print_function

import os.path
import firebase
import random
import copy

from utils import __tokens_per_rarity, __level_to_rarity_ordinal
from utils import *
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ITEM_FIELD_RARITY = "rarity"
ITEM_FIELD_NAME = "name"
ITEM_FIELD_PRICE = "price"
ITEM_FIELD_ATTUNEMENT = "attunement"
ITEM_FIELD_RARITY_LEVEL = "rarity_level"

SHOP_ITEM_FIELD_QUANTITY = "quantity"
SHOP_ITEM_FIELD_SOLD = "sold"
SHOP_ITEM_FIELD_INDEX = "index"


def generate_new_magic_shop(character_levels_csv: str) -> str:
    magic_shop_list = __generate_random_shop_list(character_levels_csv)
    magic_shop_string = ''
    counter = 1
    for magic_item in magic_shop_list:
        if not(SHOP_ITEM_FIELD_QUANTITY in magic_item):
            magic_item[SHOP_ITEM_FIELD_QUANTITY] = 1
        magic_item[SHOP_ITEM_FIELD_SOLD] = False
        magic_item[SHOP_ITEM_FIELD_INDEX] = counter
        magic_shop_string += \
            f'{counter}) **{magic_item[ITEM_FIELD_NAME]}** - {__tokens_per_rarity(magic_item[ITEM_FIELD_RARITY], magic_item[ITEM_FIELD_RARITY_LEVEL])}\n'
        counter += 1
    firebase.set_in_magic_shop(magic_shop_list)
    return magic_shop_string


def __generate_random_shop_list(character_levels_csv: str) -> list:
    character_levels_list: list = character_levels_csv.split(',')
    character_rarity_ordinal_list = list(map(lambda it: __level_to_rarity_ordinal(int(it)), character_levels_list))
    character_rarity_ordinal_list.sort(reverse=True)
    max_rarity_ordinal = max(character_rarity_ordinal_list)
    items_from_firebase = firebase.get_all_items_from_firebase()
    filtered_items = list()
    common = list()
    uncommon = list()
    rare = list()
    very_rare = list()
    legendary = list()
    for item in items_from_firebase:
        rarity = item[ITEM_FIELD_RARITY].lower()
        if rarity == COMMON and max_rarity_ordinal >= COMMON_ORDINAL:
            common.append(item)
            filtered_items.append(item)
        elif rarity == UNCOMMON and max_rarity_ordinal >= UNCOMMON_ORDINAL:
            uncommon.append(item)
            filtered_items.append(item)
        elif rarity == RARE and max_rarity_ordinal >= RARE_ORDINAL:
            rare.append(item)
            filtered_items.append(item)
        elif rarity == VERY_RARE and max_rarity_ordinal >= VERY_RARE_ORDINAL:
            very_rare.append(item)
            filtered_items.append(item)
        elif rarity == LEGENDARY and max_rarity_ordinal >= LEGENDARY_ORDINAL:
            legendary.append(item)
            filtered_items.append(item)
    magic_shop_list = list()
    for character_rarity_ordinal in character_rarity_ordinal_list:
        if character_rarity_ordinal == COMMON_ORDINAL:
            common_item_clone = copy.deepcopy(random.choice(common))
            magic_shop_list.append(common_item_clone)
        elif character_rarity_ordinal == UNCOMMON_ORDINAL:
            uncommon_item_clone = copy.deepcopy(random.choice(uncommon))
            magic_shop_list.append(uncommon_item_clone)
        elif character_rarity_ordinal == RARE_ORDINAL:
            rare_item_clone = copy.deepcopy(random.choice(rare))
            magic_shop_list.append(rare_item_clone)
        elif character_rarity_ordinal == VERY_RARE_ORDINAL:
            very_rare_item_clone = copy.deepcopy(random.choice(very_rare))
            magic_shop_list.append(very_rare_item_clone)
        elif character_rarity_ordinal == LEGENDARY_ORDINAL:
            legendary_item_clone = copy.deepcopy(random.choice(legendary))
            magic_shop_list.append(legendary_item_clone)

    rest_items = random.sample(filtered_items, 16)
    for item in rest_items:
        magic_shop_list.append(item)
    potion_item = {
        ITEM_FIELD_NAME: "Potion of healing 2d4+2 (infinite amount)",
        ITEM_FIELD_PRICE: "50 gp",
        ITEM_FIELD_RARITY: "Common",
        ITEM_FIELD_ATTUNEMENT: "NO",
        ITEM_FIELD_RARITY_LEVEL: "MINOR",
        SHOP_ITEM_FIELD_QUANTITY: infinite_quantity
    }
    magic_shop_list.append(potion_item)
    return magic_shop_list


def get_current_shop_string(items) -> str:
    final_string = ''
    for item in items:
        if item[SHOP_ITEM_FIELD_SOLD] is False:
            final_string += f'{item[SHOP_ITEM_FIELD_INDEX]}) **{item[ITEM_FIELD_NAME]}** - {__tokens_per_rarity(item[ITEM_FIELD_RARITY], item[ITEM_FIELD_RARITY_LEVEL])}\n'
        else:
            final_string += f'~~{item[SHOP_ITEM_FIELD_INDEX]}) {item[ITEM_FIELD_NAME]} - {__tokens_per_rarity(item[ITEM_FIELD_RARITY], item[ITEM_FIELD_RARITY_LEVEL])}~~ SOLD\n'
    return final_string


def sell_item(index) -> str:
    items = firebase.get_magic_shop_items()
    sold = False
    for item in items:
        if item[SHOP_ITEM_FIELD_QUANTITY] != infinite_quantity and item[SHOP_ITEM_FIELD_INDEX] == index and item[SHOP_ITEM_FIELD_SOLD] is False:
            item[SHOP_ITEM_FIELD_QUANTITY] = item[SHOP_ITEM_FIELD_QUANTITY] - 1
            quantity = item[SHOP_ITEM_FIELD_QUANTITY]
            if quantity < 0:
                raise Exception("Item quantity reached.")
            if quantity == 0:
                sold = True
                item[SHOP_ITEM_FIELD_SOLD] = True
    if sold:
        firebase.set_in_magic_shop(items)
        return get_current_shop_string(items)
    else:
        return ""


def refresh_shop_string() -> str:
    return get_current_shop_string(firebase.get_magic_shop_items())


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
            token_cost = '1 common token' if len(row) < 3 else __tokens_per_rarity(row[2], row[4])
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
                    f'"{ITEM_FIELD_NAME}":"{row[0]}","{ITEM_FIELD_PRICE}":"{row[1]}","{ITEM_FIELD_RARITY}":"{row[2]}","{ITEM_FIELD_ATTUNEMENT}":"{row[3]}","{ITEM_FIELD_RARITY_LEVEL}":"{row[5]}"')
                items.write('},')

        items.write(']')
