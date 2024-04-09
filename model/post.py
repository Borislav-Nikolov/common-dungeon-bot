class Post:
    def __init__(self, post_id: str, post_group_name: str, last_editor: str):
        self.post_id: str = post_id
        self.post_group_name: str = post_group_name
        self.last_editor: str = last_editor
