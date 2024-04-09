from model.postsection import PostSection
from model.post import Post
from provider import postsprovider
from util import utils
from typing import Optional
from provider import rolepermissionsprovider
from model.role import Role


arrow_up_emoji = '\U00002B06'
arrow_down_emoji = '\U00002B07'
edit_emoji = '\U0000270F'


ALLOWED_POST_GROUPS = ['post', 'lore']


def get_permissions_action_name(post_group_name: str) -> str:
    return f'{post_group_name}_posting_permissions'


def add_post(posts_channel_id, post_message_id, post_group_name, post_creator_id):
    post_section: PostSection
    try:
        post_section = postsprovider.get_post_section(posts_channel_id)
    except ValueError:
        post_section = PostSection(
            post_section_id=posts_channel_id,
            posts=list[Post]()
        )
    post_section.posts.append(
        Post(
            post_id=str(post_message_id),
            post_group_name=post_group_name,
            last_editor=str(post_creator_id)
        )
    )
    postsprovider.update_post_section(post_section)


def remove_post(posts_channel_id, post_message_id) -> bool:
    # TODO: pass section as an argument
    post_section: PostSection = postsprovider.get_post_section_group(posts_channel_id, post_message_id)
    index = utils.find_index(post_section.posts, lambda post: post.post_id == str(post_message_id))
    if index != -1:
        post_section.posts.pop(index)
        postsprovider.update_post_section(post_section)
        return True
    return False


def get_post_before(posts_channel_id, post_message_id) -> Optional[Post]:
    # TODO: pass section as an argument
    post_section: PostSection = postsprovider.get_post_section_group(posts_channel_id, post_message_id)
    posts_count = len(post_section.posts)
    if posts_count <= 1:
        return None
    index_of_pivot = utils.find_index(post_section.posts, lambda post: post.post_id == str(post_message_id))
    if index_of_pivot >= 1:
        return post_section.posts[index_of_pivot - 1]
    return None


def get_post_after(posts_channel_id, post_message_id) -> Optional[Post]:
    # TODO: pass section as an argument
    post_section: PostSection = postsprovider.get_post_section_group(posts_channel_id, post_message_id)
    posts_count = len(post_section.posts)
    if posts_count <= 1:
        return None
    index_of_pivot = utils.find_index(post_section.posts, lambda post: post.post_id == str(post_message_id))
    if index_of_pivot != -1 and index_of_pivot != posts_count - 1:
        return post_section.posts[index_of_pivot + 1]
    return None


def is_group_allowed(group_name: str) -> bool:
    return utils.find_index(ALLOWED_POST_GROUPS, lambda it: it == group_name) != -1


def any_has_permissions(post_group_name: str, role_ids: list[int]):
    post_group_permissions_name = get_permissions_action_name(post_group_name)
    permitted_roles = rolepermissionsprovider.get_permitted_roles(post_group_permissions_name)
    for role_id in role_ids:
        if has_permissions(role_id, permitted_roles):
            return True
    return False


def has_permissions(role_id, permitted_roles: list[Role]) -> bool:
    role_id_str = str(role_id)
    return utils.find_index(permitted_roles, lambda it: it.role_id == role_id_str) != -1


def add_permitted_role(post_group_name: str, role_id) -> bool:
    role_id_str = str(role_id)
    post_group_permissions_name = get_permissions_action_name(post_group_name)
    return rolepermissionsprovider.add(post_group_permissions_name, role_id_str)


def remove_permitted_role(post_group_name: str, role_id) -> bool:
    role_id_str = str(role_id)
    post_group_permissions_name = get_permissions_action_name(post_group_name)
    return rolepermissionsprovider.remove(post_group_permissions_name, role_id_str)
