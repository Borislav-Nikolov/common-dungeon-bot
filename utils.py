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


def __rarity_to_ordinal(rarity: str) -> int:
    rarity = rarity.lower()
    if rarity == COMMON:
        return COMMON_ORDINAL
    elif rarity == UNCOMMON:
        return UNCOMMON_ORDINAL
    elif rarity == RARE:
        return RARE_ORDINAL
    elif rarity == VERY_RARE:
        return VERY_RARE_ORDINAL
    elif rarity == LEGENDARY:
        return LEGENDARY_ORDINAL
    else:
        raise Exception(f'Unsupported rarity: {rarity}')


def __level_to_rarity_ordinal(level: int) -> int:
    if __in_range(level, 1, 5):
        return UNCOMMON_ORDINAL
    elif __in_range(level, 6, 10):
        return RARE_ORDINAL
    elif __in_range(level, 11, 15):
        return VERY_RARE_ORDINAL
    elif __in_range(level, 16, 20):
        return LEGENDARY_ORDINAL
    else:
        raise Exception(f'Level out of range: {level}')


def __tokens_per_rarity_number(rarity, rarity_level) -> int:
    tokens_per_rarity = __tokens_per_rarity(rarity, rarity_level)
    first_symbol = tokens_per_rarity[0:1]
    second_symbol = tokens_per_rarity[1:2]
    final_number_string = ""
    if first_symbol.isnumeric():
        final_number_string += first_symbol
    if second_symbol.isnumeric():
        final_number_string += second_symbol
    if len(final_number_string) == 0:
        raise Exception("No token price could be derived.")
    return int(final_number_string)


def __tokens_per_rarity(rarity, rarity_level) -> str:
    rarity = rarity.lower()
    rarity_level = rarity_level.lower()
    if rarity == COMMON:
        return '1 common token'
    elif rarity == UNCOMMON and rarity_level == TYPE_MINOR:
        return '3 uncommon tokens'
    elif rarity == UNCOMMON and rarity_level == TYPE_MAJOR:
        return '6 uncommon tokens'
    elif rarity == RARE and rarity_level == TYPE_MINOR:
        return '4 rare tokens'
    elif rarity == RARE and rarity_level == TYPE_MAJOR:
        return '8 rare tokens'
    elif rarity == VERY_RARE and rarity_level == TYPE_MINOR:
        return '5 very rare tokens'
    elif rarity == VERY_RARE and rarity_level == TYPE_MAJOR:
        return '10 very rare tokens'
    elif rarity == LEGENDARY and rarity_level == TYPE_MINOR:
        return '5 legendary tokens'
    elif rarity == LEGENDARY and rarity_level == TYPE_MAJOR:
        return '10 legendary tokens'


def __in_range(compared, first, last) -> bool:
    if first >= last:
        raise Exception("The first number in range should be bigger than the last.")
    return first <= compared <= last


def __strip_id_tag(player_id_tag: str) -> str:
    return player_id_tag.strip()[2:player_id_tag.find('>')]
