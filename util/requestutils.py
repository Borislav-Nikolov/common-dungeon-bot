from util import utils

REQUEST_RARITY_NAME_COMMON = "common"
REQUEST_RARITY_NAME_UNCOMMON = "uncommon"
REQUEST_RARITY_NAME_RARE = "rare"
REQUEST_RARITY_NAME_VERY_RARE = "veryrare"
REQUEST_RARITY_NAME_LEGENDARY = "legendary"


def translate_rarity_name(name) -> str:
    name_lower = name.lower()
    if name_lower == REQUEST_RARITY_NAME_COMMON.lower() or name_lower == utils.COMMON.lower():
        return REQUEST_RARITY_NAME_COMMON
    elif name_lower == REQUEST_RARITY_NAME_UNCOMMON.lower() or name_lower == utils.UNCOMMON.lower():
        return REQUEST_RARITY_NAME_UNCOMMON
    elif name_lower == REQUEST_RARITY_NAME_RARE.lower() or name_lower == utils.RARE.lower():
        return REQUEST_RARITY_NAME_RARE
    elif name_lower == REQUEST_RARITY_NAME_VERY_RARE.lower() or name_lower == utils.VERY_RARE.lower():
        return REQUEST_RARITY_NAME_VERY_RARE
    elif name_lower == REQUEST_RARITY_NAME_LEGENDARY.lower() or name_lower == utils.LEGENDARY.lower():
        return REQUEST_RARITY_NAME_LEGENDARY
    return ""
