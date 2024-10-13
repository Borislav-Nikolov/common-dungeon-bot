from firebase_admin import db
from source.sourcefields import *
import json
import copy

global items_ref
global items_ref_2


def init_items_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global items_ref_2
    items_ref_2 = db.reference(f"all_items2")


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
def mix_all_items_and_all_items_2():
    items: list = items_ref.get()
    items2: list = items_ref_2.get()
    new_list: list = copy.deepcopy(items2)
    for item in items:
        rarity_level = item[field_rarity_level]
        if rarity_level == 'MINOR':
            item[field_rarity_level] = init_TYPE_MINOR
        elif rarity_level == 'MAJOR':
            item[field_rarity_level] = init_TYPE_MAJOR
        has_match = False
        for item2 in items2:
            name1 = item[field_name]
            name2 = item2[field_name]
            if name1 == name2 or name1 in name2 or name2 in name1 or name1[:7] in name2 or name2[:7] in name1:
                has_match = True
        if not has_match:
            new_list.append(item)
    items_ref_2.set(new_list)


def init_in_firebase():
    new_items = list()
    with open('items_update.json', 'r', encoding='utf-8') as items:
        items_json = json.load(items)
        items_list = items_json['item']
        grouped_items_list = items_json['itemGroup']
    for item in items_list:
        append_new_item(new_items, item)
    for item in grouped_items_list:
        if field_items in item and len(item[field_items]) > 0:
            for specific_name in item[field_items]:
                fixed_name = specific_name.split("|")[0]
                item_copy = copy.deepcopy(item)
                item_copy[field_name] = fixed_name
                append_new_item(new_items, item_copy)
    items_ref_2.set(new_items)


def append_new_item(new_items: list, item):
    if field_name in item and len(item[field_name]) > 0 and field_source in item and item[
            field_source] in permitted_sources and field_rarity in item and item[field_rarity] in permitted_rarities:
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
            field_rarity_level: item[field_tier] if field_tier in item and item[field_tier] in permitted_rarity_levels
            else init_TYPE_MAJOR,
            "description": description_from_entries(item[field_entries]) if field_entries in item
            else "missing description"
        })


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
field_rarity_level = "rarity_level"

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
