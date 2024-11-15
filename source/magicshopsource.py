from firebase_admin import db


global shop_ref


def init_shop_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global shop_ref
    shop_ref = db.reference(f"{prefix}/magic_shop_items")


def get_magic_shop_items() -> list:
    return shop_ref.get()


def set_in_magic_shop(items: list):
    shop_ref.set(items)
