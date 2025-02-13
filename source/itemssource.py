from firebase_admin import db
from source.sourcefields import *
import json
import copy
import re

global items_ref
global items_ref_2


def init_items_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global items_ref_2
    items_ref_2 = db.reference(f"all_items2")


def get_all_items() -> list:
    return list(items_ref_2.get().values())


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
    items2: list = list(items_ref_2.get().values())
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
            item['consumable'] = item[field_name] in consumable_items
            new_list.append(item)
    items_ref_2.set({item['name']: item for item in new_list})


def init_in_firebase():
    new_items = list()
    with open('items_update.json', 'r', encoding='utf-8') as items:
        items_json = json.load(items)
        items_list = items_json['item']
        grouped_items_list = items_json['itemGroup']
    for item in items_list:
        append_new_item(new_items, item)
    for item in grouped_items_list:
        if field_items in item and len(item[field_items]) > 0 and field_entries in item:
            for specific_name in item[field_items]:
                fixed_name = specific_name.split("|")[0]
                item_copy = copy.deepcopy(item)
                item_copy[field_name] = fixed_name
                append_new_item(new_items, item_copy)
    items_ref_2.set({item['name']: item for item in new_items})


def extract_to_json():
    data = {
        "items": []
    }
    with open('items_update.json', 'r', encoding='utf-8') as items:
        items_json = json.load(items)
        items_list = items_json['item']
        grouped_items_list = items_json['itemGroup']
        for item in items_list:
            if field_source in item and item[field_source] in permitted_sources:
                data["items"].append(item)
        for item in grouped_items_list:
            if field_source in item and item[field_source] in permitted_sources:
                data["items"].append(item)
    with open('filtered_items.json', 'w', encoding='utf-8') as items_file_write:
        json.dump(data, items_file_write, indent=4)


def append_new_item(new_items: list, item):
    if field_name in item and len(item[field_name]) > 0 and item[field_name] not in prohibited_items_by_name and \
            field_source in item and item[field_source] in permitted_sources and field_rarity in item and item[
            field_rarity] in permitted_rarities:

        if field_entries in item and isinstance(item[field_entries], list) and len(item[field_entries]) > 0 and \
                isinstance(item[field_entries][0], str) and '#itemEntry' in item[field_entries][0]:
            return

        translation_table = str.maketrans('', '', '$#[]/.')
        translated_item_name = item['name'].translate(translation_table)
        new_items.append({
            "name": translated_item_name,
            "attunement": True if field_req_attune in item and ((isinstance(item[field_req_attune], bool) and item[
                field_req_attune]) or (isinstance(item[field_req_attune], str) and len(item[field_req_attune]) > 0))
            else False,
            "banned": translated_item_name in banned_items,
            "official": True,
            "price": "undetermined",
            "rarity": item[field_rarity],
            field_rarity_level: extract_rarity_level(item, translated_item_name),
            "description": description_from_entries(item[field_entries]) if field_entries in item
            else "*missing description*",
            "consumable": translated_item_name in consumable_items
        })


def extract_rarity_level(item, translated_item_name) -> str:
    return init_TYPE_MINOR if should_be_minor(translated_item_name) else item[field_tier] \
        if field_tier in item and item[field_tier] in permitted_rarity_levels else init_TYPE_MAJOR


def should_be_minor(item_name) -> bool:
    return any(partial_name in item_name for partial_name in partial_names_of_items_to_be_made_minor)


def description_from_entries(entries: list[str, dict]) -> str:
    final_string = ''
    for entry in entries:
        if isinstance(entry, str):
            final_string += f'{entry}\n'
        elif isinstance(entry, dict):
            if field_type in entry and entry[field_type] == 'entries' and field_entries in entry:
                final_string += f'**{entry[field_name]}**\n{description_from_entries(entry[field_entries])}\n'
            elif field_type in entry and entry[field_type] == 'list':
                for description_entry in entry[field_items]:
                    description_value = description_entry
                    if isinstance(description_value, dict) and field_type in description_value and description_value[
                            field_type] == 'item' and field_name in description_value and field_entries in\
                            description_value:
                        description_value = f'**{description_value[field_name]}.** ' \
                                            f'{description_from_entries(description_value[field_entries])}'
                    final_string += f'- {description_value}\n'
            elif field_type in entry and entry[field_type] == 'table':
                col_labels: list[str] = entry['colLabels']
                number_of_cols = len(col_labels)
                rows: list[list[str]] = entry['rows']
                for row in rows:
                    for i in range(0, number_of_cols):
                        label = col_labels[i]
                        value = row[i]
                        if isinstance(value, dict) and 'roll' in value and 'exact' in value['roll']:
                            value = value['roll']['exact']
                        final_string += f'**{label}:** {value}\n'
                    final_string += '\n'
    return replace_text(final_string)


def replace_text(input_string):
    return re.sub(r'{@\w+ ([^|}]*)[^}]*}', r'\1', input_string)


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
                     'ERLW', 'MOT', 'SCC', 'AAG', 'SatO',
                     'HotDQ', 'PotA', 'OotA', 'SKT', 'TftYP', 'ToA', 'WDH', 'WDMM',
                     'GoS', 'BGDiA', 'IDRotF', 'CM', 'WBtW', 'DSotDQ', 'PaBTSO']

prohibited_items_by_name = [
    'Horned Ring', 'Korolnor Scepter', 'Mind Crystal (Subtle)'
]

partial_names_of_items_to_be_made_minor = [
    'Devastation Orb of', 'Mind Crystal'
]

banned_items = [
    'Deck of Wonder'
]

consumable_items = [
    "Ammunition (+1) (Per)",
    "Ammunition (+2) (Per)",
    "Ammunition (+3) (Per)",
    "Arrow of Slaying",
    "Walloping Ammunition",

    "Bag of Beans",
    "Bead of Force",
    "Bead of Nourishment",
    "Bead of Refreshment",
    "Chime of Opening",
    "Devastation Orb of Air",
    "Devastation Orb of Earth",
    "Devastation Orb of Fire",
    "Devastation Orb of Water",
    "Dust of Disappearance",
    "Dust of Dryness",
    "Dust of Sneezing and Choking",
    "Elemental Gem, Blue Sapphire",
    "Elemental Gem, Emerald",
    "Elemental Gem, Red Corundum",
    "Elemental Gem, Yellow Diamond",
    "Elixir of Health",
    "Keoghtom's Ointment",
    "Mind Crystal (Careful)",
    "Mind Crystal (Distant)",
    "Mind Crystal (Empowered)",
    "Mind Crystal (Extended)",
    "Mind Crystal (Heightened)",
    "Mind Crystal (Quickened)",
    "Mystery Key",
    "Necklace of Fireballs",
    "Nolzur's Marvelous Pigments",
    "Oil of Etherealness",
    "Oil of Sharpness",
    "Oil of Slipperiness",
    "Perfume of Bewitching",
    "Philter of Love",
    "Pot of Awakening",

    "Potion of Animal Friendship",
    "Potion of Clairvoyance",
    "Potion of Climbing",
    "Potion of Cloud Giant Strength",
    "Potion of Diminution",
    "Potion of Fire Breath",
    "Potion of Fire Giant Strength",
    "Potion of Flying",
    "Potion of Frost Giant Strength",
    "Potion of Gaseous Form",
    "Potion of Greater Healing",
    "Potion of Growth",
    "Potion of Healing",
    "Potion of Heroism",
    "Potion of Hill Giant Strength",
    "Potion of Invisibility",
    "Potion of Invulnerability",
    "Potion of Longevity",
    "Potion of Mind Reading",
    "Potion of Poison",
    "Potion of Speed",
    "Potion of Stone Giant Strength",
    "Potion of Storm Giant Strength",
    "Potion of Superior Healing",
    "Potion of Supreme Healing",
    "Potion of Vitality",
    "Potion of Water Breathing",

    "Robe of Useful Items",
    "Scroll of Protection from Aberrations",
    "Scroll of Protection from Beasts",
    "Scroll of Protection from Celestials",
    "Scroll of Protection from Elementals",
    "Scroll of Protection from Fey",
    "Scroll of Protection from Fiends",
    "Scroll of Protection from Plants",
    "Scroll of Protection from Undead",
    "Sovereign Glue",

    "Spell Scroll (Cantrip)",
    "Spell Scroll (1st Level)",
    "Spell Scroll (2nd Level)",
    "Spell Scroll (3rd Level)",
    "Spell Scroll (4th Level)",
    "Spell Scroll (5th Level)",
    "Spell Scroll (6th Level)",
    "Spell Scroll (7th Level)",
    "Spell Scroll (8th Level)",
    "Spell Scroll (9th Level)",

    "Universal Solvent",

    "Tome of Clear Thought",
    "Tome of Leadership and Influence",
    "Tome of Understanding",
    "Manual of Bodily Health",
    "Manual of Gainful Exercise",
    "Manual of Quickness of Action"
]

init_COMMON = "common"
init_UNCOMMON = "uncommon"
init_RARE = "rare"
init_VERY_RARE = "very rare"
init_LEGENDARY = "legendary"
init_TYPE_MINOR = "minor"
init_TYPE_MAJOR = "major"

permitted_rarities = [init_COMMON, init_UNCOMMON, init_RARE, init_VERY_RARE, init_LEGENDARY]
permitted_rarity_levels = [init_TYPE_MINOR, init_TYPE_MAJOR]
