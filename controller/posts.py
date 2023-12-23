from model.postsection import PostSection
from model.post import Post
from provider import postsprovider
from util import utils
from typing import Optional


arrow_up_emoji = '\U00002B06'
arrow_down_emoji = '\U00002B07'
edit_emoji = '\U0000270F'


def add_post(posts_channel_id, post_message_id):
    post_section: PostSection
    try:
        post_section = postsprovider.get_post_section(posts_channel_id)
    except ValueError:
        post_section = PostSection(post_section_id=posts_channel_id, posts=list[Post]())
    post_section.posts.append(Post(post_id=post_message_id))
    postsprovider.update_post_section(post_section)


def remove_post(posts_channel_id, post_message_id) -> bool:
    post_section: PostSection = postsprovider.get_post_section(posts_channel_id)
    index = utils.find_index(post_section.posts, lambda post: post.post_id == post_message_id)
    if index != -1:
        post_section.posts.pop(index)
        postsprovider.update_post_section(post_section)
        return True
    return False


def get_post_before(posts_channel_id, post_message_id) -> Optional[Post]:
    post_section: PostSection = postsprovider.get_post_section(posts_channel_id)
    posts_count = len(post_section.posts)
    if posts_count <= 1:
        return None
    index_of_pivot = utils.find_index(post_section.posts, lambda post: post.post_id == post_message_id)
    if index_of_pivot >= 1:
        return post_section.posts[index_of_pivot - 1]
    return None


def get_post_after(posts_channel_id, post_message_id) -> Optional[Post]:
    post_section: PostSection = postsprovider.get_post_section(posts_channel_id)
    posts_count = len(post_section.posts)
    if posts_count <= 1:
        return None
    index_of_pivot = utils.find_index(post_section.posts, lambda post: post.post_id == post_message_id)
    if index_of_pivot != -1 and index_of_pivot != posts_count - 1:
        return post_section.posts[index_of_pivot + 1]
    return None


def add_new_post_section(post_channel_id) -> bool:
    if postsprovider.post_section_exists(post_channel_id):
        return False
    postsprovider.add_new_post_section(post_channel_id)
    return True
