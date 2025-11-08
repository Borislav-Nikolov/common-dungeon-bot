class SessionLogPlayerData:
    """
    Represents data for a single player in a session log.
    """
    def __init__(self, player_id: str, character_name: str, class_name: str, is_dm: bool):
        self.player_id = player_id
        self.character_name = character_name
        self.class_name = class_name
        self.is_dm = is_dm

    @staticmethod
    def from_dict(data: dict):
        """
        Creates a SessionLogPlayerData instance from a dictionary.
        Expected dict structure:
        {
            'player_id': str,
            'character_name': str,
            'class_name': str,
            'is_dm': bool
        }
        """
        return SessionLogPlayerData(
            player_id=data.get('player_id', ''),
            character_name=data.get('character_name', ''),
            class_name=data.get('class_name', ''),
            is_dm=data.get('is_dm', False)
        )


class SessionLog:
    """
    Represents a complete session log entry.
    """
    def __init__(self, moderator_name: str, players: dict[str, SessionLogPlayerData]):
        self.moderator_name = moderator_name
        self.players = players  # Dict mapping player_id to SessionLogPlayerData

    @staticmethod
    def from_dict(log_data: dict):
        """
        Creates a SessionLog instance from a Firebase log dictionary.
        Expected dict structure:
        {
            'moderator_name': str,
            'player_id1': {
                'player_id': str,
                'character_name': str,
                'class_name': str,
                'is_dm': bool
            },
            'player_id2': { ... },
            ...
        }
        """
        moderator_name = log_data.get('moderator_name', '')
        players = {}

        for key, value in log_data.items():
            # Skip the moderator_name key
            if key == 'moderator_name':
                continue

            # Parse player data
            if isinstance(value, dict) and 'player_id' in value:
                player_data = SessionLogPlayerData.from_dict(value)
                players[key] = player_data

        return SessionLog(moderator_name=moderator_name, players=players)
