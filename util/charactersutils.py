CHARACTER_STATUS_ACTIVE = "active"
CHARACTER_STATUS_INACTIVE = "inactive"
CHARACTER_STATUS_DEAD = "dead"
VALID_CHARACTER_STATUSES = [CHARACTER_STATUS_ACTIVE, CHARACTER_STATUS_INACTIVE, CHARACTER_STATUS_DEAD]


PARAMETER_NAME = "name"
PARAMETER_CHARACTER = "character"
PARAMETER_CLASS = "class"
PARAMETER_LEVEL = "level"


def character_status_to_visibility(status: str) -> bool:
    return status == CHARACTER_STATUS_ACTIVE


def is_character_status_valid(status: str) -> bool:
    return status in VALID_CHARACTER_STATUSES


def status_label(status: str) -> str:
    if not is_character_status_valid(status):
        raise Exception(f'Invalid status: {status}')
    if status == CHARACTER_STATUS_ACTIVE:
        return 'Active'
    elif status == CHARACTER_STATUS_INACTIVE:
        return 'Inactive'
    elif status == CHARACTER_STATUS_DEAD:
        return 'Dead'
    else:
        raise Exception(f'Invalid status: {status}')


def status_description(status: str) -> str:
    if not is_character_status_valid(status):
        raise Exception(f'Invalid status: {status}')
    if status == CHARACTER_STATUS_ACTIVE:
        return 'The character is being actively played.'
    elif status == CHARACTER_STATUS_INACTIVE:
        return 'The character is not or cannot be played.'
    elif status == CHARACTER_STATUS_DEAD:
        return 'The character is dead.'
    else:
        raise Exception(f'Invalid status: {status}')


def status_emoji(status: str) -> str:
    if not is_character_status_valid(status):
        raise Exception(f'Invalid status: {status}')
    if status == CHARACTER_STATUS_ACTIVE:
        return '\U00002705'
    elif status == CHARACTER_STATUS_INACTIVE:
        return '\U000023F8'
    elif status == CHARACTER_STATUS_DEAD:
        return '\U0001F480'
    else:
        raise Exception(f'Invalid status: {status}')
