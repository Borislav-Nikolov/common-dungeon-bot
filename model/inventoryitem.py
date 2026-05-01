from model.item import Item
from model.rarity import Rarity
from typing import Optional


class InventoryItem(Item):
    def __init__(self, name: str, description: str, price: str, rarity: Rarity, attunement: bool, consumable: bool,
                 official: bool, banned: bool, always_available: bool, quantity: int, index: int, sellable: bool,
                 variants: Optional[list[str]] = None, variant: Optional[str] = None,
                 current_holder: Optional[str] = None):
        super().__init__(
            name=name,
            description=description,
            price=price,
            rarity=rarity,
            attunement=attunement,
            consumable=consumable,
            official=official,
            banned=banned,
            always_available=always_available,
            variants=variants
        )
        self.quantity: int = quantity
        self.index: int = index
        self.sellable: bool = sellable
        self.variant: Optional[str] = variant
        self.current_holder: Optional[str] = current_holder

