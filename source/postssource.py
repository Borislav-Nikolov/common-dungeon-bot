from api import postsrequests


def get_posts(post_section_id) -> dict:
    return postsrequests.get_posts(post_section_id)


def get_all_posts() -> dict:
    return postsrequests.get_all_posts()


def update_in_posts(posts_data):
    return postsrequests.update_in_posts(posts_data)
