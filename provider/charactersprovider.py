from model.player import Player
from model.character import Character
from model.characterclass import CharacterClass
from model.inventoryitem import InventoryItem
from model.item import Item
from model.inventorymessage import InventoryMessage
from model.rarity import rarity_strings_to_rarity, Rarity
from model.playerrole import PlayerRole, player_role_from_name
from model.playerstatus import PlayerStatus, player_status_from_name
from source.sourcefields import *
from source import playerssource
from util import utils, charactersutils
from typing import Optional

from util.utils import split_strip


def add_or_update_player(player: Player):
    add_or_update_players([player])


def add_or_update_players(players: list[Player]):
    player_data = dict()
    for player in players:
        player_data[player.player_id] = {
            PLAYER_FIELD_NAME: player.name,
            PLAYER_FIELD_PLAYER_ROLE: player.player_role.name,
            PLAYER_FIELD_PLAYER_STATUS: player.player_status.name,
            PLAYER_FIELD_PLAYER_LEVEL: player.player_level,
            PLAYER_FIELD_SESSIONS_ON_THIS_LEVEL: player.sessions_on_this_level,
            PLAYER_FIELD_COMMON_TOKENS: player.common_tokens,
            PLAYER_FIELD_UNCOMMON_TOKENS: player.uncommon_tokens,
            PLAYER_FIELD_RARE_TOKENS: player.rare_tokens,
            PLAYER_FIELD_VERY_RARE_TOKENS: player.very_rare_tokens,
            PLAYER_FIELD_LEGENDARY_TOKENS: player.legendary_tokens,
            PLAYER_FIELD_RESERVED_ITEMS: list(
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
                        ITEM_FIELD_ALWAYS_AVAILABLE: item.always_available
                    },
                    player.reserved_items
                )
            ),
            PLAYER_FIELD_INVENTORY_MESSAGES: {f'i{inventory_message.beginning_index}': inventory_message.message_id
                                              for inventory_message in player.inventory_messages},
            PLAYER_FIELD_RESERVED_ITEMS_MESSAGES: {
                f'i{reserved_items_message.beginning_index}': reserved_items_message.message_id
                for reserved_items_message in player.reserved_items_messages}
        }
        if player.inventory is not None:
            player_data[player.player_id][PLAYER_FIELD_INVENTORY] = list(
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
                        ITEM_FIELD_ALWAYS_AVAILABLE: item.always_available,
                        INVENTORY_ITEM_FIELD_QUANTITY: item.quantity,
                        INVENTORY_ITEM_FIELD_INDEX: item.index,
                        INVENTORY_ITEM_FIELD_SELLABLE: item.sellable
                    },
                    player.inventory
                )
            )
        if player.characters is not None:
            player_data[player.player_id][PLAYER_FIELD_CHARACTERS] = list(
                map(
                    lambda character: {
                        CHARACTER_FIELD_NAME: character.character_name,
                        CHARACTER_FIELD_LEVEL: character.character_level,
                        CHARACTER_FIELD_MAX_LEVEL: character.max_level,
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
                        CHARACTER_FIELD_SESSIONS: character.sessions_on_this_level,
                        CHARACTER_FIELD_STATUS: character.status
                    },
                    player.characters
                )
            )
        if player.last_bundle_rarity:
            player_data[player.player_id][PLAYER_FIELD_LAST_BUNDLE_RARITY] =\
                f'{player.last_bundle_rarity.rarity},{player.last_bundle_rarity.rarity_level}'
    playerssource.update_in_players(player_data)


def get_player(player_id) -> Optional[Player]:
    player_data = playerssource.get_player(player_id)
    if player_data:
        return map_player_object(player_id, player_data)
    else:
        return None


def get_players(player_ids, include_inventory=True, include_characters=True) -> dict[str, Player]:
    players_data = playerssource.get_players(
        player_ids=player_ids,
        include_inventory=include_inventory,
        include_characters=include_characters
    )
    return {player_id: map_player_object(player_id, players_data[player_id]) for player_id in players_data}


def get_all_players() -> list[Player]:
    players_data = playerssource.get_all_players()
    return list(map(lambda player_id: map_player_object(player_id, players_data[player_id]), players_data))


def delete_player(player_id):
    playerssource.delete_player(player_id)


def map_player_object(player_id, player_data: dict) -> Player:
    reserved_items = utils.filter_not_none(
        list() if PLAYER_FIELD_RESERVED_ITEMS not in player_data else player_data[PLAYER_FIELD_RESERVED_ITEMS]
    )
    last_bundle_rarity: Optional[Rarity] = None
    if PLAYER_FIELD_LAST_BUNDLE_RARITY in player_data:
        rarity_and_level = split_strip(player_data[PLAYER_FIELD_LAST_BUNDLE_RARITY], ',')
        last_bundle_rarity = rarity_strings_to_rarity(rarity_and_level[0], rarity_and_level[1])
    return Player(
        player_id=player_id,
        name=player_data[PLAYER_FIELD_NAME],
        player_status=PlayerStatus.Active if PLAYER_FIELD_PLAYER_STATUS not in player_data else player_status_from_name(
            player_data[PLAYER_FIELD_PLAYER_STATUS]),
        player_role=PlayerRole.Regular if PLAYER_FIELD_PLAYER_ROLE not in player_data else player_role_from_name(
            player_data[PLAYER_FIELD_PLAYER_ROLE]),
        player_level=-1 if PLAYER_FIELD_PLAYER_LEVEL not in player_data else player_data[PLAYER_FIELD_PLAYER_LEVEL],
        sessions_on_this_level=-1 if PLAYER_FIELD_SESSIONS_ON_THIS_LEVEL not in player_data else player_data[
            PLAYER_FIELD_SESSIONS_ON_THIS_LEVEL],
        common_tokens=player_data[PLAYER_FIELD_COMMON_TOKENS],
        uncommon_tokens=player_data[PLAYER_FIELD_UNCOMMON_TOKENS],
        rare_tokens=player_data[PLAYER_FIELD_RARE_TOKENS],
        very_rare_tokens=player_data[PLAYER_FIELD_VERY_RARE_TOKENS],
        legendary_tokens=player_data[PLAYER_FIELD_LEGENDARY_TOKENS],
        last_bundle_rarity=last_bundle_rarity,
        characters=None if PLAYER_FIELD_CHARACTERS not in player_data else list(
            map(
                lambda character: Character(
                    character_name=character[CHARACTER_FIELD_NAME],
                    character_level=character[CHARACTER_FIELD_LEVEL],
                    max_level=20 if CHARACTER_FIELD_MAX_LEVEL not in character else character[CHARACTER_FIELD_MAX_LEVEL],
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
                    sessions_on_this_level=character[CHARACTER_FIELD_SESSIONS],
                    status=charactersutils.CHARACTER_STATUS_ACTIVE if CHARACTER_FIELD_STATUS not in character else
                    character[CHARACTER_FIELD_STATUS]
                ),
                player_data[PLAYER_FIELD_CHARACTERS]
            )
        ),
        inventory=None if PLAYER_FIELD_INVENTORY not in player_data else list(
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
                    always_available=False if ITEM_FIELD_ALWAYS_AVAILABLE not in item else item[
                        ITEM_FIELD_ALWAYS_AVAILABLE],
                    quantity=item[INVENTORY_ITEM_FIELD_QUANTITY],
                    index=item[INVENTORY_ITEM_FIELD_INDEX],
                    sellable=True if INVENTORY_ITEM_FIELD_SELLABLE not in item else item[INVENTORY_ITEM_FIELD_SELLABLE]
                ),
                utils.filter_not_none(player_data[PLAYER_FIELD_INVENTORY])
            )
        ),
        reserved_items=list(
            map(
                lambda item: Item(
                    name=item[ITEM_FIELD_NAME],
                    description=item[ITEM_FIELD_DESCRIPTION],
                    price=item[ITEM_FIELD_PRICE],
                    rarity=rarity_strings_to_rarity(item[ITEM_FIELD_RARITY], item[ITEM_FIELD_RARITY_LEVEL]),
                    attunement=item[ITEM_FIELD_ATTUNEMENT],
                    consumable=False if ITEM_FIELD_CONSUMABLE not in item else item[ITEM_FIELD_CONSUMABLE],
                    official=False if ITEM_FIELD_OFFICIAL not in item else item[ITEM_FIELD_OFFICIAL],
                    banned=False if ITEM_FIELD_BANNED not in item else item[ITEM_FIELD_BANNED],
                    always_available=False if ITEM_FIELD_ALWAYS_AVAILABLE not in item else item[
                        ITEM_FIELD_ALWAYS_AVAILABLE]
                ),
                reserved_items
            )
        ),
        inventory_messages=list(
            map(
                lambda key: InventoryMessage(
                    beginning_index=int(key[1:]),
                    message_id=player_data[PLAYER_FIELD_INVENTORY_MESSAGES][key]
                ),
                player_data[PLAYER_FIELD_INVENTORY_MESSAGES]
            )
        ) if PLAYER_FIELD_INVENTORY_MESSAGES in player_data else list(),
        reserved_items_messages=list(
            map(
                lambda key: InventoryMessage(
                    beginning_index=int(key[1:]),
                    message_id=player_data[PLAYER_FIELD_RESERVED_ITEMS_MESSAGES][key]
                ),
                player_data[PLAYER_FIELD_RESERVED_ITEMS_MESSAGES]
            )
        ) if PLAYER_FIELD_RESERVED_ITEMS_MESSAGES in player_data else list(),
    )
