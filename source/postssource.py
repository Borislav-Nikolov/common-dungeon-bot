from firebase_admin import db


global post_sections_ref


def init_posts_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global post_sections_ref
    post_sections_ref = db.reference(f"{prefix}/posts")


def get_posts(post_section_id) -> list:
    string_id = str(post_section_id)
    return post_sections_ref.order_by_key().equal_to(string_id).get()[string_id]


def update_in_posts(posts_data):
    post_sections_ref.update(posts_data)
