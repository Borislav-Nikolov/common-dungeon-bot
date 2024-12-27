from model.character import Character
from model.inventoryitem import InventoryItem
from model.inventorymessage import InventoryMessage
from model.reserveditemmessage import ReservedItemMessage
from model.item import Item
from model.playerrole import PlayerRole
from model.playerstatus import PlayerStatus
from util.utils import *
from typing import Optional


class Player:
    def __init__(self, player_id, name: str, player_role: PlayerRole, player_status: PlayerStatus, player_level: int,
                 sessions_on_this_level: int, common_tokens: int,
                 uncommon_tokens: int, rare_tokens: int, very_rare_tokens: int, legendary_tokens: int,
                 characters: Optional[list[Character]], inventory: Optional[list[InventoryItem]],
                 reserved_items: list[Item], inventory_messages: list[InventoryMessage],
                 reserved_items_messages: list[ReservedItemMessage]):
        self.player_id = player_id
        self.name: str = name
        self.player_role: PlayerRole = player_role
        self.player_status: PlayerStatus = player_status
        self.player_level: int = player_level
        self.sessions_on_this_level: int = sessions_on_this_level
        self.common_tokens: int = common_tokens
        self.uncommon_tokens: int = uncommon_tokens
        self.rare_tokens: int = rare_tokens
        self.very_rare_tokens: int = very_rare_tokens
        self.legendary_tokens: int = legendary_tokens
        self.characters: Optional[list[Character]] = characters
        self.inventory: Optional[list[InventoryItem]] = inventory
        self.reserved_items: list[Item] = reserved_items
        self.inventory_messages: list[InventoryMessage] = inventory_messages
        self.reserved_items_messages: list[ReservedItemMessage] = reserved_items_messages

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
