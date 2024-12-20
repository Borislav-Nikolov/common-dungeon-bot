from enum import Enum
from typing import Optional


class PlayerRole(Enum):
    Regular = 1
    Moderator = 2
    Admin = 3


def player_role_from_name(player_role_name: str) -> Optional[PlayerRole]:
    player_role_name_lower = player_role_name.lower()
    if player_role_name_lower == PlayerRole.Regular.name.lower():
        return PlayerRole.Regular
    elif player_role_name_lower == PlayerRole.Moderator.name.lower():
        return PlayerRole.Moderator
    elif player_role_name_lower == PlayerRole.Admin.name.lower():
        return PlayerRole.Admin
    else:
        return None
