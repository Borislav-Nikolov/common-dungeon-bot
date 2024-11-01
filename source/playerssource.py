from firebase_admin import db


global players_ref
global players_path


def init_players_source(is_test: bool):
    prefix = "/test" if is_test else ""
    global players_path
    players_path = f"{prefix}/players"
    global players_ref
    players_ref = db.reference(players_path)


def get_player(player_id) -> dict:
    string_id = str(player_id)
    return players_ref.order_by_key().equal_to(string_id).get()[string_id]


def get_players(player_ids: list) -> dict:
    player_list = dict()
    all_players = players_ref.get()
    for player_id in all_players:
        if player_id in player_ids:
            player_list[player_id] = all_players[player_id]
    return player_list


def get_all_players() -> dict:
    return players_ref.get()


def update_in_players(player_data):
    players_ref.update(player_data)


def delete_player(player_id):
    player_ref = db.reference(f'{players_path}/{player_id}')
    player_ref.delete()
