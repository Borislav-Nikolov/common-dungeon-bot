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

EMOJI_RARITY_COMMON = '\U000026AA'
EMOJI_RARITY_UNCOMMON = '\U0001F7E2'
EMOJI_RARITY_RARE = '\U0001F535'
EMOJI_RARITY_VERY_RARE = '\U0001F7E3'
EMOJI_RARITY_LEGENDARY = '\U0001F7E1'
# this is a red X, used in place of other emojis when they are missing so that the rest of the text remains aligned.
EMOJI_NONE = '\U0000274C'


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


def sessions_to_next_level(current_level) -> str:
    current_level_int = int(current_level)
    if 1 <= current_level_int <= 2:
        return "1"
    elif 3 <= current_level_int <= 4:
        return "2"
    else:
        return "3"


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
    if index == 1:
        return EMOJI_A
    if index == 2:
        return EMOJI_B
    if index == 3:
        return EMOJI_C
    if index == 4:
        return EMOJI_D
    if index == 5:
        return EMOJI_E
    if index == 6:
        return EMOJI_F
    if index == 7:
        return EMOJI_G
    if index == 8:
        return EMOJI_H
    if index == 9:
        return EMOJI_I
    if index == 10:
        return EMOJI_J
    if index == 11:
        return EMOJI_K
    if index == 12:
        return EMOJI_L
    if index == 13:
        return EMOJI_M
    if index == 14:
        return EMOJI_N
    if index == 15:
        return EMOJI_O
    if index == 16:
        return EMOJI_P
    if index == 17:
        return EMOJI_Q
    if index == 18:
        return EMOJI_R
    if index == 19:
        return EMOJI_S
    if index == 20:
        return EMOJI_T
    if index == 21:
        return EMOJI_U
    if index == 22:
        return EMOJI_V
    if index == 23:
        return EMOJI_W
    if index == 24:
        return EMOJI_X
    if index == 25:
        return EMOJI_Y
    if index == 26:
        return EMOJI_Z
    return EMOJI_NONE

def emoji_to_index(emoji: str) -> int:
    if emoji == EMOJI_A:
        return 1
    if emoji == EMOJI_B:
        return 2
    if emoji == EMOJI_C:
        return 3
    if emoji == EMOJI_D:
        return 4
    if emoji == EMOJI_E:
        return 5
    if emoji == EMOJI_F:
        return 6
    if emoji == EMOJI_G:
        return 7
    if emoji == EMOJI_H:
        return 8
    if emoji == EMOJI_I:
        return 9
    if emoji == EMOJI_J:
        return 10
    if emoji == EMOJI_K:
        return 11
    if emoji == EMOJI_L:
        return 12
    if emoji == EMOJI_M:
        return 13
    if emoji == EMOJI_N:
        return 14
    if emoji == EMOJI_O:
        return 15
    if emoji == EMOJI_P:
        return 16
    if emoji == EMOJI_Q:
        return 17
    if emoji == EMOJI_R:
        return 18
    if emoji == EMOJI_S:
        return 19
    if emoji == EMOJI_T:
        return 20
    if emoji == EMOJI_U:
        return 21
    if emoji == EMOJI_V:
        return 22
    if emoji == EMOJI_W:
        return 23
    if emoji == EMOJI_X:
        return 24
    if emoji == EMOJI_Y:
        return 25
    if emoji == EMOJI_Z:
        return 26


def get_rarity_emoji(rarity: str) -> str:
    switcher = {
        COMMON: EMOJI_RARITY_COMMON,
        UNCOMMON: EMOJI_RARITY_UNCOMMON,
        RARE: EMOJI_RARITY_RARE,
        VERY_RARE: EMOJI_RARITY_VERY_RARE,
        LEGENDARY: EMOJI_RARITY_LEGENDARY,
    }
    return switcher.get(rarity.lower(), EMOJI_NONE)
