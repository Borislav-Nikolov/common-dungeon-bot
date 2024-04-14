from model.role import Role
from source import rolepermissionssourse
from util import utils


def add(action_name: str, role_id) -> bool:
    role_id_str = str(role_id)
    previous_roles = rolepermissionssourse.get_permitted_roles(action_name)
    if previous_roles is None:
        previous_roles = list()
    # do not add if already contained
    if utils.find_index(previous_roles, lambda it: it == role_id_str) != -1:
        return False
    previous_roles.append(role_id_str)
    rolepermissionssourse.update_permitted_roles(action_name, previous_roles)
    return True


def remove(action_name: str, role_id) -> bool:
    role_id_str = str(role_id)
    previous_roles = rolepermissionssourse.get_permitted_roles(action_name)
    if previous_roles is not None:
        index = utils.find_index(previous_roles, lambda it: it == role_id_str)
        if index == -1:
            return False
        previous_roles.pop(index)
        rolepermissionssourse.update_permitted_roles(action_name, previous_roles)
        return True
    return False


def get_permitted_roles(action_name: str) -> list[Role]:
    roles = rolepermissionssourse.get_permitted_roles(action_name)
    if roles is not None:
        return list(map(lambda role_str: Role(role_str), roles))
    return list()
