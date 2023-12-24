from source import postssource
from model.post import Post
from model.postsection import PostSection


def get_post_section(post_section_id) -> PostSection:
    try:
        posts_data = postssource.get_posts(post_section_id)
    except KeyError:
        raise ValueError("Post section not found.")
    return PostSection(
        post_section_id=post_section_id,
        posts=list(map(lambda it: Post(post_id=it), posts_data))
    )


def post_section_exists(post_section_id) -> bool:
    if postssource.get_posts(post_section_id) is None:
        return False
    return True


def update_post_section(post_section_id: PostSection):
    postssource.update_in_posts(
        posts_data={
            post_section_id.post_section_id: list(map(lambda it: it.post_id, post_section_id.posts))
        }
    )


def add_new_post_section(post_section_id: PostSection):
    postssource.update_in_posts(posts_data={post_section_id: list()})
