from model.item import Item
from model.rarity import Rarity


class InventoryItem(Item):
    def __init__(self, name: str, description: str, price: str, rarity: Rarity, attunement: bool, consumable: bool,
                 official: bool, banned: bool, quantity: int, index: int):
        super().__init__(
            name=name,
            description=description,
            price=price,
            rarity=rarity,
            attunement=attunement,
            consumable=consumable,
            official=official,
            banned=banned
        )
        self.quantity: int = quantity
        self.index: int = index

