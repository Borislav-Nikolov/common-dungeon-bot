from model.characterclass import CharacterClass


class Character:
    def __init__(self, character_name: str, character_level: int, max_level: int,
                 classes: list[CharacterClass], last_dm: str,
                 sessions_on_this_level: int, status: str):
        self.character_name: str = character_name
        self.character_level: int = character_level
        self.max_level: int = max_level
        self.classes: list[CharacterClass] = classes
        self.last_dm: str = last_dm
        self.sessions_on_this_level: int = sessions_on_this_level
        self.status = status
