import discord

import firebase
import magicshop
import characters


def run_discord_bot(bot_token):
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            if str(message.content).startswith('1)') or str(message.content).startswith('~~'):
                firebase.set_shop_message_id(message.id)  # TODO do not use firebase directly
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        await handle_help_requests(message)
        await handle_server_initialization_prompts(message)
        await handle_shop_commands(message)
        await handle_character_commands(message)

    client.run(bot_token)


async def handle_help_requests(message):
    help_key = '$help'
    if str(message.content) == help_key:
        commands_message = "General commands:\n" \
                           "    In the Shop channel:\n" \
                           "        1) $shop.*number* (for instance $shop.12) buys an item from the shop that" \
                           "corresponds to the given number.\n" \
                           "\n" \
                           "Admin commands:\n" \
                           "    In any channel:\n" \
                           "        1) $init.shop - initializes the current channel as the Shop channel.\n" \
                           "        2) $init.characters.info - initializes the current channel as the Characters" \
                           "Info channel\n" \
                           "    In the Shop channel:\n" \
                           "        1) $shop.generate.[...]* - generates a new Magic Shop list.\n" \
                           "            *Instead of '[...]' type the character levels that you want the items to be" \
                           " generated for. Separate the levels by comma (',')"
        await message.author.send(commands_message)


async def handle_server_initialization_prompts(message):
    init_key = '$init.'
    full_message = str(message.content)
    if full_message.startswith(init_key) and is_admin(message):
        init_key_length = len(init_key)
        init_message = full_message[init_key_length:]
        if init_message == 'shop':
            firebase.set_shop_channel_id(message.channel.id)
            await message.channel.send('Channel initialized as the Shop channel.')
        elif init_message == 'characters.info':
            firebase.set_character_info_channel_id(message.channel.id)
            await message.channel.send('Channel initialized as the Characters Info channel.')


async def handle_shop_commands(message):
    shop_key = '$shop'
    keywords = str(message.content).split('.')
    if keywords[0] == shop_key and message.channel.id == firebase.get_shop_channel_id():
        command_message = keywords[1]
        if command_message == 'generate' and is_admin(message):
            character_levels_csv = keywords[2]
            await message.channel.send(magicshop.generate_new_magic_shop(character_levels_csv))
        elif command_message.isnumeric():
            shop_message = await message.channel.fetch_message(firebase.get_shop_message_id())
            shop_string = magicshop.sell_item(int(command_message))
            if len(shop_string) > 0:
                await shop_message.edit(content=shop_string)
                await message.add_reaction('🪙')
            else:
                await message.add_reaction('❌')


async def handle_character_commands(message):
    characters_key = '$characters'
    keywords = str(message.content).split('.')
    if keywords[0] == characters_key:
        characters.set_player(keywords[1])


def is_admin(message) -> bool:
    return message.author.guild_permissions.administrator
