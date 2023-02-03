from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

randomized_item_list_spreadsheet = '1nnB8VmIUtkYCIQXcaQIsEHj10K7OkELYRloSJmbK-Ow'
randomized_item_list_spreadsheet_range = 'Magic Shop!A2:E'


def get_item_names() -> str:
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
        result = sheet.values().get(spreadsheetId=randomized_item_list_spreadsheet,
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


COMMON = "common"
UNCOMMON = "uncommon"
RARE = "rare"
VERY_RARE = "very rare"
LEGENDARY = "legendary"
TYPE_MINOR = "minor"
TYPE_MAJOR = "major"


def tokens_per_rarity(rarity, rarity_type) -> str:
    rarity = rarity.lower()
    rarity_type = rarity_type.lower()
    if rarity == COMMON:
        '1 common token'
    elif rarity == UNCOMMON and rarity_type == TYPE_MINOR:
        '3 uncommon tokens'
    elif rarity == UNCOMMON and rarity_type == TYPE_MAJOR:
        '6 uncommon tokens'
    elif rarity == RARE and rarity_type == TYPE_MINOR:
        '4 rare tokens'
    elif rarity == RARE and rarity_type == TYPE_MAJOR:
        '8 rare tokens'
    elif rarity == VERY_RARE and rarity_type == TYPE_MINOR:
        '5 very rare tokens'
    elif rarity == VERY_RARE and rarity_type == TYPE_MAJOR:
        '10 very rare tokens'
    elif rarity == LEGENDARY and rarity_type == TYPE_MINOR:
        '5 legendary tokens'
    elif rarity == LEGENDARY and rarity_type == TYPE_MAJOR:
        '10 legendary tokens'
