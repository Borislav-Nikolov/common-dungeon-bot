from firebase_admin import db
from typing import Optional


global role_permissions_ref


def init_role_permissions_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global role_permissions_ref
    role_permissions_ref = db.reference(f"{prefix}/role_permissions")


def get_permitted_roles(action_name: str) -> Optional[list]:
    data = role_permissions_ref.order_by_key().equal_to(action_name).get()
    return data[action_name] if len(data) != 0 else None


def update_permitted_roles(action_name: str, roles: list[str]):
    role_permissions_ref.update({action_name: roles})

