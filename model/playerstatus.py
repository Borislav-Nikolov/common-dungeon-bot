from enum import Enum
from typing import Optional


class PlayerStatus(Enum):
    Banned = 1
    Inactive = 2
    Active = 3


def player_status_from_name(player_status_name: str) -> Optional[PlayerStatus]:
    player_status_name_lower = player_status_name.lower()
    if player_status_name_lower == PlayerStatus.Banned.name.lower():
        return PlayerStatus.Banned
    elif player_status_name_lower == PlayerStatus.Inactive.name.lower():
        return PlayerStatus.Inactive
    elif player_status_name_lower == PlayerStatus.Active.name.lower():
        return PlayerStatus.Active
    else:
        return None
