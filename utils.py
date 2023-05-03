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


EMOJI_A = '\U0001F1E6'
EMOJI_B = '\U0001F1E7'
EMOJI_C = '\U0001F1E8'
EMOJI_D = '\U0001F1E9'
EMOJI_E = '\U0001F1EA'
EMOJI_F = '\U0001F1EB'
EMOJI_G = '\U0001F1EC'
EMOJI_H = '\U0001F1ED'
EMOJI_I = '\U0001F1EE'
EMOJI_J = '\U0001F1EF'
EMOJI_K = '\U0001F1F0'
EMOJI_L = '\U0001F1F1'
EMOJI_M = '\U0001F1F2'
EMOJI_N = '\U0001F1F3'
EMOJI_O = '\U0001F1F4'
EMOJI_P = '\U0001F1F5'
EMOJI_Q = '\U0001F1F6'
EMOJI_R = '\U0001F1F7'
EMOJI_S = '\U0001F1F8'
EMOJI_T = '\U0001F1F9'
EMOJI_U = '\U0001F1FA'
EMOJI_V = '\U0001F1FB'
EMOJI_W = '\U0001F1FC'
EMOJI_X = '\U0001F1FD'
EMOJI_Y = '\U0001F1FE'
EMOJI_Z = '\U0001F1FF'

letter_emojis = (EMOJI_A, EMOJI_B, EMOJI_C, EMOJI_D, EMOJI_E, EMOJI_F, EMOJI_G, EMOJI_H, EMOJI_I, EMOJI_J, EMOJI_K,
                 EMOJI_L, EMOJI_M, EMOJI_N, EMOJI_O, EMOJI_P, EMOJI_Q, EMOJI_R, EMOJI_S, EMOJI_T, EMOJI_U, EMOJI_V,
                 EMOJI_W, EMOJI_X, EMOJI_Y, EMOJI_Z)


def rarity_to_ordinal(rarity: str) -> int:
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


def level_to_rarity_ordinal(level: int) -> int:
    if in_range(level, 1, 5):
        return UNCOMMON_ORDINAL
    elif in_range(level, 6, 10):
        return RARE_ORDINAL
    elif in_range(level, 11, 15):
        return VERY_RARE_ORDINAL
    elif in_range(level, 16, 20):
        return LEGENDARY_ORDINAL
    else:
        raise Exception(f'Level out of range: {level}')


def tokens_per_rarity_number(rarity, rarity_level) -> int:
    tokens_per_rarity_string = tokens_per_rarity(rarity, rarity_level)
    first_symbol = tokens_per_rarity_string[0:1]
    second_symbol = tokens_per_rarity_string[1:2]
    final_number_string = ""
    if first_symbol.isnumeric():
        final_number_string += first_symbol
    if second_symbol.isnumeric():
        final_number_string += second_symbol
    if len(final_number_string) == 0:
        raise Exception("No token price could be derived.")
    return int(final_number_string)


def tokens_per_rarity(rarity, rarity_level) -> str:
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


def sessions_to_next_level(current_level) -> int:
    current_level_int = int(current_level)
    if 1 <= current_level_int <= 2:
        return 1
    elif 3 <= current_level_int <= 4:
        return 2
    else:
        return 3


def in_range(compared, first, last) -> bool:
    if first >= last:
        raise Exception("The first number in range should be bigger than the last.")
    return first <= compared <= last


def strip_id_tag(player_id_tag: str) -> str:
    return player_id_tag.strip()[2:player_id_tag.find('>')]


def split_strip(string_data: str, delimiter: str) -> list:
    return list(map(lambda it: it.strip(), string_data.split(delimiter)))


def first_line(string: str) -> str:
    new_line_index = string.find('\n')
    if new_line_index == -1:
        return string
    else:
        return string[0:new_line_index]


def index_to_emoji(index: int) -> str:
    return letter_emojis[index - 1]


def emoji_to_index(emoji: str) -> int:
    return letter_emojis.index(emoji) + 1
