from model.character import Character
from model.inventoryitem import InventoryItem
from model.inventorymessage import InventoryMessage
from util.utils import *


class Player:
    def __init__(self, player_id, name: str, common_tokens: int, uncommon_tokens: int, rare_tokens: int,
                 very_rare_tokens: int, legendary_tokens: int, characters: list[Character],
                 inventory: list[InventoryItem], inventory_messages: list[InventoryMessage]):
        self.player_id = player_id
        self.name: str = name
        self.common_tokens: int = common_tokens
        self.uncommon_tokens: int = uncommon_tokens
        self.rare_tokens: int = rare_tokens
        self.very_rare_tokens: int = very_rare_tokens
        self.legendary_tokens: int = legendary_tokens
        self.characters: list[Character] = characters
        self.inventory: list[InventoryItem] = inventory
        self.inventory_messages: list[InventoryMessage] = inventory_messages

    def get_tokens_with_rarity_string(self, rarity: str) -> int:
        return self.get_tokens_with_rarity_ordinal(rarity_to_ordinal(rarity))

    def get_tokens_with_rarity_ordinal(self, rarity_ordinal: int) -> int:
        if rarity_ordinal == COMMON_ORDINAL:
            return self.common_tokens
        elif rarity_ordinal == UNCOMMON_ORDINAL:
            return self.uncommon_tokens
        elif rarity_ordinal == RARE_ORDINAL:
            return self.rare_tokens
        elif rarity_ordinal == VERY_RARE_ORDINAL:
            return self.very_rare_tokens
        elif rarity_ordinal == LEGENDARY_ORDINAL:
            return self.legendary_tokens

    def set_tokens_with_rarity_string(self, rarity: str, new_value: int):
        return self.set_tokens_with_rarity_ordinal(rarity_to_ordinal(rarity), new_value)

    def set_tokens_with_rarity_ordinal(self, rarity_ordinal: int, new_value: int):
        if rarity_ordinal == COMMON_ORDINAL:
            self.common_tokens = new_value
        elif rarity_ordinal == UNCOMMON_ORDINAL:
            self.uncommon_tokens = new_value
        elif rarity_ordinal == RARE_ORDINAL:
            self.rare_tokens = new_value
        elif rarity_ordinal == VERY_RARE_ORDINAL:
            self.very_rare_tokens = new_value
        elif rarity_ordinal == LEGENDARY_ORDINAL:
            self.legendary_tokens = new_value
