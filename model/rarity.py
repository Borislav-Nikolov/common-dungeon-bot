from enum import Enum
from util.utils import *


class Rarity(Enum):
    COMMON_MINOR = (COMMON, TYPE_MINOR)
    COMMON_MAJOR = (COMMON, TYPE_MAJOR)
    UNCOMMON_MINOR = (UNCOMMON, TYPE_MINOR)
    UNCOMMON_MAJOR = (UNCOMMON, TYPE_MAJOR)
    RARE_MINOR = (RARE, TYPE_MINOR)
    RARE_MAJOR = (RARE, TYPE_MAJOR)
    VERY_RARE_MINOR = (VERY_RARE, TYPE_MINOR)
    VERY_RARE_MAJOR = (VERY_RARE, TYPE_MAJOR)
    LEGENDARY_MINOR = (LEGENDARY, TYPE_MINOR)
    LEGENDARY_MAJOR = (LEGENDARY, TYPE_MAJOR)

    def __init__(self, rarity: str, rarity_level: str):
        self.rarity: str = rarity
        self.rarity_level: str = rarity_level


def rarity_strings_to_rarity(rarity: str, rarity_level: str) -> Rarity:
    rarity = rarity.casefold()
    rarity_level = rarity_level.casefold()
    if rarity == COMMON.casefold() and rarity_level == TYPE_MINOR.casefold():
        return Rarity.COMMON_MINOR
    elif rarity == COMMON.casefold() and rarity_level == TYPE_MAJOR.casefold():
        return Rarity.COMMON_MAJOR
    elif rarity == UNCOMMON.casefold() and rarity_level == TYPE_MINOR.casefold():
        return Rarity.UNCOMMON_MINOR
    elif rarity == UNCOMMON.casefold() and rarity_level == TYPE_MAJOR.casefold():
        return Rarity.UNCOMMON_MAJOR
    elif rarity == RARE.casefold() and rarity_level == TYPE_MINOR.casefold():
        return Rarity.RARE_MINOR
    elif rarity == RARE.casefold() and rarity_level == TYPE_MAJOR.casefold():
        return Rarity.RARE_MAJOR
    elif rarity == VERY_RARE.casefold() and rarity_level == TYPE_MINOR.casefold():
        return Rarity.VERY_RARE_MINOR
    elif rarity == VERY_RARE.casefold() and rarity_level == TYPE_MAJOR.casefold():
        return Rarity.VERY_RARE_MAJOR
    elif rarity == LEGENDARY.casefold() and rarity_level == TYPE_MINOR.casefold():
        return Rarity.LEGENDARY_MINOR
    elif rarity == LEGENDARY.casefold() and rarity_level == TYPE_MAJOR.casefold():
        return Rarity.LEGENDARY_MAJOR
