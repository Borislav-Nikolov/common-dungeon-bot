from model.player import Player
from model.character import Character
from model.characterclass import CharacterClass
from model.inventoryitem import InventoryItem
from model.rarity import rarity_strings_to_rarity
from provider.sourcefields import *
from source import playerssource


def add_or_update_player(player: Player):
    add_or_update_players([player])


def add_or_update_players(players: list[Player]):
    player_data = dict()
    for player in players:
        player_data[player.player_id] = {
            PLAYER_FIELD_NAME: player.name,
            PLAYER_FIELD_COMMON_TOKENS: player.common_tokens,
            PLAYER_FIELD_UNCOMMON_TOKENS: player.uncommon_tokens,
            PLAYER_FIELD_RARE_TOKENS: player.rare_tokens,
            PLAYER_FIELD_VERY_RARE_TOKENS: player.very_rare_tokens,
            PLAYER_FIELD_LEGENDARY_TOKENS: player.legendary_tokens,
            PLAYER_FIELD_CHARACTERS: list(
                map(
                    lambda character: {
                        CHARACTER_FIELD_NAME: character.character_name,
                        CHARACTER_FIELD_LEVEL: character.character_level,
                        CHARACTER_FIELD_CLASSES: list(
                            map(
                                lambda character_class: {
                                    CLASS_FIELD_NAME: character_class.class_name,
                                    CLASS_FIELD_LEVEL: character_class.level,
                                    CLASS_FIELD_IS_PRIMARY: character_class.is_primary
                                },
                                character.classes
                            )
                        ),
                        CHARACTER_FIELD_LAST_DM: character.last_dm,
                        CHARACTER_FIELD_SESSIONS: character.sessions_on_this_level
                    },
                    player.characters
                )
            ),
            PLAYER_FIELD_INVENTORY: list(
                map(
                    lambda item: {
                        ITEM_FIELD_NAME: item.name,
                        ITEM_FIELD_DESCRIPTION: item.description,
                        ITEM_FIELD_PRICE: item.price,
                        ITEM_FIELD_RARITY: item.rarity.rarity,
                        ITEM_FIELD_RARITY_LEVEL: item.rarity.rarity_level,
                        ITEM_FIELD_ATTUNEMENT: item.attunement,
                        ITEM_FIELD_CONSUMABLE: item.consumable,
                        ITEM_FIELD_OFFICIAL: item.official,
                        ITEM_FIELD_BANNED: item.banned,
                        INVENTORY_ITEM_FIELD_QUANTITY: item.quantity,
                        INVENTORY_ITEM_FIELD_INDEX: item.index
                    },
                    player.inventory
                )
            )
        }
    playerssource.update_in_players(player_data)


def get_player(player_id) -> Player:
    player_data = playerssource.get_player(player_id)
    return map_player_object(player_id, player_data)


def get_players(player_ids: list) -> list[Player]:
    players_data = playerssource.get_players(player_ids)
    return list(map(lambda player_id: map_player_object(player_id, players_data[player_id]), players_data))


def map_player_object(player_id, player_data: dict) -> Player:
    return Player(
        player_id=player_id,
        name=player_data[PLAYER_FIELD_NAME],
        common_tokens=player_data[PLAYER_FIELD_COMMON_TOKENS],
        uncommon_tokens=player_data[PLAYER_FIELD_UNCOMMON_TOKENS],
        rare_tokens=player_data[PLAYER_FIELD_RARE_TOKENS],
        very_rare_tokens=player_data[PLAYER_FIELD_VERY_RARE_TOKENS],
        legendary_tokens=player_data[PLAYER_FIELD_LEGENDARY_TOKENS],
        characters=list(
            map(
                lambda character: Character(
                    character_name=character[CHARACTER_FIELD_NAME],
                    character_level=character[CHARACTER_FIELD_LEVEL],
                    classes=list(
                        map(
                            lambda character_class: CharacterClass(
                                class_name=character_class[CLASS_FIELD_NAME],
                                level=character_class[CLASS_FIELD_LEVEL],
                                is_primary=character_class[CLASS_FIELD_IS_PRIMARY]
                            ),
                            character[CHARACTER_FIELD_CLASSES]
                        )
                    ),
                    last_dm=character[CHARACTER_FIELD_LAST_DM],
                    sessions_on_this_level=character[CHARACTER_FIELD_SESSIONS]
                ),
                player_data[PLAYER_FIELD_CHARACTERS]
            )
        ),
        inventory=list(
            map(
                lambda item: InventoryItem(
                    name=item[ITEM_FIELD_NAME],
                    description=item[ITEM_FIELD_DESCRIPTION],
                    price=item[ITEM_FIELD_PRICE],
                    rarity=rarity_strings_to_rarity(item[ITEM_FIELD_RARITY], item[ITEM_FIELD_RARITY_LEVEL]),
                    attunement=item[ITEM_FIELD_ATTUNEMENT],
                    consumable=False if ITEM_FIELD_CONSUMABLE not in item else item[ITEM_FIELD_CONSUMABLE],
                    official=False if ITEM_FIELD_OFFICIAL not in item else item[ITEM_FIELD_OFFICIAL],
                    banned=False if ITEM_FIELD_BANNED not in item else item[ITEM_FIELD_BANNED],
                    quantity=item[INVENTORY_ITEM_FIELD_QUANTITY],
                    index=item[INVENTORY_ITEM_FIELD_INDEX]
                ),
                list() if PLAYER_FIELD_INVENTORY not in player_data else player_data[PLAYER_FIELD_INVENTORY]
            )
        )
    )
