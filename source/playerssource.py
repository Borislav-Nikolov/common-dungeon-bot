from typing import Optional
from api import charactersrequests


def get_player(player_id, include_inventory=True, include_characters=True) -> Optional[dict]:
    return charactersrequests.get_player(
        player_id=player_id,
        include_inventory=include_inventory,
        include_characters=include_characters
    )


def get_players(player_ids, include_inventory=True, include_characters=True) -> dict:
    return charactersrequests.get_players(
        player_ids=player_ids,
        include_inventory=include_inventory,
        include_characters=include_characters
    )


def get_all_players(include_inventory=True, include_characters=True) -> dict:
    return charactersrequests.get_all_players(
        include_inventory=include_inventory,
        include_characters=include_characters
    )


def update_in_players(players_data):
    return charactersrequests.update_in_players(players_data)


def delete_player(player_id):
    return charactersrequests.delete_player(player_id)
