from util import botutils, utils
from api import rolesrequests


async def handle_roles_prompts(message) -> bool:
    role_key = '$role'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == role_key and botutils.is_admin_message(message):
        if keywords[1] == 'moderator':
            await handle_set_moderator_role(message, keywords[2])
        return True
    return False


async def handle_set_moderator_role(message, role_id_tag):
    # Strip the Discord role tag to get the bare role ID
    role_id = botutils.strip_role_id_tag(role_id_tag)

    # Set the moderator role ID in the backend
    if rolesrequests.set_moderator_role_id(role_id):
        await message.add_reaction('🪙')
    else:
        await message.add_reaction('❌')
