from typing import Optional
from api import rolepermissionsrequests


def get_permitted_roles(action_name: str) -> Optional[list]:
    return rolepermissionsrequests.get_permitted_roles(action_name)


def update_permitted_roles(action_name: str, roles: list[str]):
    rolepermissionsrequests.update_permitted_roles(action_name, roles)
