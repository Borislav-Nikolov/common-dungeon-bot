from model.rarity import Rarity
from typing import Optional


class Item:
    def __init__(self, name: str, description: str, price: str, rarity: Rarity, attunement: bool, consumable: bool,
                 official: bool, banned: bool, always_available: bool, variants: Optional[list[str]] = None):
        self.name: str = name
        self.description: str = description
        self.price: str = price
        self.rarity: Rarity = rarity
        self.attunement: bool = attunement
        self.consumable: bool = consumable
        self.official: bool = official
        self.banned: bool = banned
        self.always_available: bool = always_available
        self.variants: Optional[list[str]] = variants
