from source import postssource, sourcefields
from model.post import Post
from model.postsection import PostSection


def get_post_section(post_section_id) -> PostSection:
    try:
        posts_data = postssource.get_posts(post_section_id)
    except KeyError:
        raise ValueError("Post section not found.")
    return PostSection(
        post_section_id=post_section_id,
        posts=list(
            map(
                lambda it: Post(
                    post_id=it,
                    post_group_name=posts_data[it][sourcefields.POST_FIELD_GROUP_NAME],
                    last_editor=posts_data[it][sourcefields.POST_FIELD_LAST_EDITOR]
                ),
                posts_data
            )
        )
    )


def get_post_section_group(post_section_id, post_id) -> PostSection:
    post_id_str = str(post_id)
    try:
        posts_data = postssource.get_posts(post_section_id)
    except KeyError:
        raise ValueError("Post section not found.")
    post_group_name = posts_data[post_id_str][sourcefields.POST_FIELD_GROUP_NAME]
    filtered_posts = list[Post]()
    for post_key in posts_data:
        current_post_group_name = posts_data[post_key][sourcefields.POST_FIELD_GROUP_NAME]
        if post_group_name == current_post_group_name:
            filtered_posts.append(
                Post(
                    post_id=post_key,
                    post_group_name=current_post_group_name,
                    last_editor=posts_data[post_id_str][sourcefields.POST_FIELD_LAST_EDITOR])
            )
    return PostSection(
        post_section_id=post_section_id,
        posts=filtered_posts
    )


def post_section_exists(post_section_id) -> bool:
    try:
        postssource.get_posts(post_section_id)
        return True
    except KeyError:
        return False


def update_post_section(post_section: PostSection):
    posts = dict()
    for post in post_section.posts:
        posts[post.post_id] = {
            sourcefields.POST_FIELD_GROUP_NAME: post.post_group_name,
            sourcefields.POST_FIELD_LAST_EDITOR: post.last_editor
        }
    postssource.update_in_posts(
        posts_data={
            post_section.post_section_id: posts
        }
    )
