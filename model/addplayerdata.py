from __future__ import annotations
from util import utils, charactersutils


class AddPlayerData:
    def __init__(self, player_id, player_name: str, character_name: str, class_name: str):
        self.player_id = player_id
        self.player_name = player_name
        self.character_name = character_name
        self.class_name = class_name

    # expected: player_id: <@1234> player_data_list: name=SomeName,character=CharName,class=Rogue
    @staticmethod
    def from_command(player_id: str, player_data_list: list) -> AddPlayerData:
        player_data = dict()
        player_data[player_id] = dict()
        player_name = ''
        character_name = ''
        class_name = ''
        for parameter in player_data_list:
            field_to_argument = utils.split_strip(parameter, '=')
            field = field_to_argument[0]
            argument = field_to_argument[1]
            if field == charactersutils.PARAMETER_NAME:
                player_name = argument
            elif field == charactersutils.PARAMETER_CHARACTER:
                character_name = argument
            elif field == charactersutils.PARAMETER_CLASS:
                class_name = argument
        if len(player_name) == 0 or len(character_name) == 0 or len(class_name) == 0:
            raise Exception("Invalid new player input provided.")
        return AddPlayerData(player_id=player_id, player_name=player_name, character_name=character_name,
                             class_name=class_name)
