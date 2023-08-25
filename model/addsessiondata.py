import model
from util import utils


class AddSessionData:
    def __init__(self, player_id, character_name, class_name, is_dm: bool):
        self.player_id = player_id
        self.character_name = character_name
        self.class_name = class_name
        self.is_dm: bool = is_dm

    @staticmethod
    def id_to_data_from_command_input(command_input: str) -> dict[str, model.addsessiondata.AddSessionData]:
        id_to_add_session_data = dict()
        for single_player_data in utils.split_strip(command_input, ','):
            single_player_data_list = utils.split_strip(single_player_data, '-')
            player_id = utils.strip_id_tag(single_player_data_list[0])
            id_to_add_session_data[player_id] = AddSessionData(
                player_id=player_id,
                character_name=single_player_data_list[1],
                class_name=single_player_data_list[2] if len(single_player_data_list) > 2 else None,
                is_dm=len(id_to_add_session_data) == 0
            )
        return id_to_add_session_data
