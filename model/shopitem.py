from model.inventoryitem import InventoryItem
from model.rarity import Rarity


class ShopItem(InventoryItem):
    def __init__(self, name: str, description: str, price: str, rarity: Rarity, attunement: bool, consumable: bool,
                 official: bool, banned: bool, quantity: int, index: int, sold: bool):
        super().__init__(
            name=name,
            description=description,
            price=price,
            rarity=rarity,
            attunement=attunement,
            consumable=consumable,
            official=official,
            banned=banned,
            quantity=quantity,
            index=index
        )
        self.sold: bool = sold
