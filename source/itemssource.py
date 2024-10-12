from firebase_admin import db
from source.sourcefields import *
import json

global items_ref_2


def init_items_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global items_ref_2
    items_ref_2 = db.reference(f"{prefix}/all_items2")


def get_all_items() -> list:
    return items_ref_2.get()


def update_in_items(item_data):
    items_ref_2.update(item_data)


def get_all_minor_items():
    return sorted(
        items_ref_2.order_by_child(ITEM_FIELD_RARITY_LEVEL).equal_to("minor").get().values(),
        key=lambda value: value[ITEM_FIELD_NAME]
    )


def get_all_major_items():
    return sorted(
        items_ref_2.order_by_child(ITEM_FIELD_RARITY_LEVEL).equal_to("major").get().values(),
        key=lambda value: value[ITEM_FIELD_NAME]
    )


# All of bellow's script is used to initialize the items in the database.
def init_in_firebase():
    new_items = list()
    with open('items_update.json', 'r', encoding='utf-8') as items:
        items_list = json.load(items)['item']
    for item in items_list:
        if field_name in item and len(item[field_name]) > 0 and field_source in item and item[field_source] in permitted_sources and field_rarity in item and item[field_rarity] in permitted_rarities:
            translation_table = str.maketrans('', '', '$#[]/.')
            item_name = item['name'].translate(translation_table)
            new_items.append({
                "name": item_name,
                "attunement": True if field_req_attune in item and ((isinstance(item[field_req_attune], bool) and item[
                    field_req_attune]) or (isinstance(item[field_req_attune], str) and len(item[field_req_attune]) > 0))
                else False,
                "banned": False,
                "official": True,
                "price": "undetermined",
                "rarity": item[field_rarity],
                "rarity_level": item[field_tier] if field_tier in item and item[field_tier] in permitted_rarity_levels
                else init_TYPE_MAJOR,
                "description": description_from_entries(item[field_entries]) if field_entries in item
                else "missing description"
            })
    items_ref_2.set(new_items)


def description_from_entries(entries: list[str, dict]) -> str:
    final_string = ''
    for entry in entries:
        if isinstance(entry, str):
            final_string += f'{entry}\n'
        elif isinstance(entry, dict):
            if field_type in entry and entry[field_type] == 'entries' and field_entries in entry:
                final_string += f'{description_from_entries(entry[field_entries])}\n'
            elif field_type in entry and entry[field_type] == 'list':
                for description_entry in entry[field_items]:
                    final_string += f'{description_entry}\n'
    return final_string


field_name = 'name'
field_source = 'source'
field_req_attune = 'reqAttune'
field_rarity = 'rarity'
field_tier = 'tier'
field_entries = 'entries'
field_type = 'type'
field_items = 'items'

permitted_sources = ['PHB', 'DMG', 'MM', 'VGM', 'XGE', 'MTF', 'TCE', 'FTD', 'MPMM', 'BGG', 'BMT',
                     'SCAG', 'GGR', 'AI', 'ERLW', 'EGW', 'MOT', 'VRGR', 'SCC', 'AAG', 'SatO',
                     'HotDQ', 'RoT', 'PotA', 'OotA', 'CoS', 'SKT', 'TftYP', 'ToA', 'WDH', 'WDMM',
                     'GoS', 'BGDiA', 'IDRotF', 'CM', 'WBtW', 'CRCotN', 'JTtRC', 'DSotDQ', 'KftGV',
                     'PaBTSO']


init_COMMON = "common"
init_UNCOMMON = "uncommon"
init_RARE = "rare"
init_VERY_RARE = "very rare"
init_LEGENDARY = "legendary"
init_TYPE_MINOR = "minor"
init_TYPE_MAJOR = "major"

permitted_rarities = [init_COMMON, init_UNCOMMON, init_RARE, init_VERY_RARE, init_LEGENDARY]
permitted_rarity_levels = [init_TYPE_MINOR, init_TYPE_MAJOR]
