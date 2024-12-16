from __future__ import annotations
from util import utils, charactersutils


class AddCharacterDataClass:
    def __init__(self, class_name: str, class_level: int):
        self.class_name: str = class_name
        self.class_level: int = class_level


class AddCharacterData:
    def __init__(self, player_id, character_name: str, character_level: int, classes_data: list[AddCharacterDataClass]):
        self.player_id = player_id
        self.character_name: str = character_name
        self.character_level: int = character_level
        self.classes_data: list[AddCharacterDataClass] = classes_data

    # expected: player_id: <@1234> character_data_list: name=SomeName,class=Rogue,level=2,class=Wizard,level=1,etc.
    @staticmethod
    def from_command(player_id: str, character_data_list: list) -> AddCharacterData:
        character_name = ''
        character_level = 0
        classes_to_level = dict()
        for parameter in character_data_list:
            key_to_value = utils.split_strip(parameter, '=')
            if key_to_value[0] == charactersutils.PARAMETER_NAME:
                character_name = key_to_value[1]
            elif key_to_value[0] == charactersutils.PARAMETER_CLASS:
                classes_to_level[key_to_value[1]] = 0
            elif key_to_value[0] == charactersutils.PARAMETER_LEVEL:
                for class_name in classes_to_level:
                    if classes_to_level[class_name] == 0:
                        classes_to_level[class_name] = int(key_to_value[1])
                        character_level += int(key_to_value[1])
        if len(character_name.strip()) == 0 or len(classes_to_level) == 0:
            raise Exception('Invalid new character data provided')
        for class_name in classes_to_level:
            if classes_to_level[class_name] == 0 and len(classes_to_level) == 1:
                classes_to_level[class_name] = 1
                character_level += 1
            elif classes_to_level[class_name] == 0:
                raise Exception(f'Level not specified for class: {class_name}')
        return AddCharacterData(
            player_id=player_id,
            character_name=character_name,
            character_level=character_level,
            classes_data=list(
                map(
                    lambda it: AddCharacterDataClass(class_name=it, class_level=classes_to_level[it]),
                    classes_to_level
                )
            )
        )
