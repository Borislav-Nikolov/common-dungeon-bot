
import os.path
import utils
import magicshop
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
            token_cost = '1 common token' if len(row) < 3 else utils.tokens_per_rarity(row[2], row[4])
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
                    f'"{magicshop.ITEM_FIELD_NAME}":"{row[0]}","{magicshop.ITEM_FIELD_PRICE}":"{row[1]}",'
                    f'"{magicshop.ITEM_FIELD_RARITY}":'
                    f'"{row[2]}","{magicshop.ITEM_FIELD_ATTUNEMENT}":"{row[3]}",'
                    f'"{magicshop.ITEM_FIELD_RARITY_LEVEL}":"{row[5]}"')
                items.write('},')

        items.write(']')
