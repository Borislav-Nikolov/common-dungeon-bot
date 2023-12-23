from model.post import Post


class PostSection:
    def __init__(self, post_section_id: str, posts: list[Post]):
        self.post_section_id: str = post_section_id
        self.posts: list[Post] = posts
