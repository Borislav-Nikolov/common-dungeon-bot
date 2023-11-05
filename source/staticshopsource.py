from firebase_admin import db


global static_shop_ref


def init_static_shop_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global static_shop_ref
    static_shop_ref = db.reference(f"{prefix}/staticshop")


def update_in_static_shop(data: dict):
    static_shop_ref.update(data)


def get_static_shop_item(item_id: str) -> dict:
    return static_shop_ref.order_by_key().equal_to(item_id).get()[item_id]
