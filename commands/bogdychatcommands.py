from api import bogdychatrequests


async def handle_chat_bogdy_command(message) -> bool:
    command_key = "Hey Bogdy"
    if message.content.startswith(command_key):
        await message.channel.send(bogdychatrequests.chat_bogdy(message.content))
        return True
    return False
