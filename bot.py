import discord
import utils
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
            content = str(message.content)
            if content.startswith('1)') or content.startswith('~~'):
                firebase.set_shop_message_id(message.id)  # TODO do not use firebase directly
            elif content.startswith('<@'):
                firebase.set_player_message_id(utils.__strip_id_tag(content), message.id)
            return

        username = str(message.author.id)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        await handle_help_requests(message)
        await handle_server_initialization_prompts(message)
        await handle_shop_commands(message, client)
        await handle_character_commands(message, client)

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
                           " generated for. Separate the levels by comma (',')" \
                           "        2) $shop.refresh - gets the current shop items from the database, generates a new" \
                           "string and refreshes the shop message with this string."
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
        elif init_message == 'characters':
            firebase.set_character_info_channel_id(message.channel.id)
            await message.channel.send('Channel initialized as the Characters Info channel.')


async def handle_shop_commands(message, client):
    shop_key = '$shop'
    keywords = str(message.content).split('.')
    if keywords[0] == shop_key and message.channel.id == firebase.get_shop_channel_id():
        command_message = keywords[1]
        if command_message == 'generate' and is_admin(message):
            character_levels_csv = keywords[2]
            await message.channel.send(magicshop.generate_new_magic_shop(character_levels_csv))
        elif command_message == 'refresh' and is_admin(message):
            shop_message = await message.channel.fetch_message(firebase.get_shop_message_id())
            await shop_message.edit(content=magicshop.refresh_shop_string())
        elif command_message.isnumeric():
            shop_message = await message.channel.fetch_message(firebase.get_shop_message_id())
            shop_string = magicshop.sell_item(message.author.id, int(command_message))
            # TODO instead of getting the message from "sell_item" use a boolean and construct message separately
            if len(shop_string) > 0:
                await shop_message.edit(content=shop_string)
                await __refresh_player_message(client, message.author.id)
                await message.add_reaction('🪙')
            else:
                await message.add_reaction('❌')


async def __refresh_player_message(client, player_id):
    await __update_player_message(client, player_id, characters.get_up_to_date_player_message(player_id))


async def __update_player_message(client, player_id, new_message):
    players_channel = client.get_channel(firebase.get_character_info_channel_id())
    player_message_id = firebase.get_player_message_id(player_id)
    player_message = await players_channel.fetch_message(player_message_id)
    await player_message.edit(content=new_message)


async def handle_character_commands(message, client):
    characters_key = '$characters'
    keywords = str(message.content).split('.')
    if keywords[0] == characters_key:
        if keywords[1] == "hardinit":
            player_id = utils.__strip_id_tag(keywords[2])
            characters.hardinit_player(player_id, keywords[3])
            players_channel = client.get_channel(firebase.get_character_info_channel_id())
            await players_channel.send(characters.get_up_to_date_player_message(player_id))
        if message.channel.id == firebase.get_character_info_channel_id():
            if keywords[1] == "addsession":
                if characters.add_session(keywords[2]):
                    split_data = keywords[2].split(',')
                    player_ids = list(
                        map(lambda it: utils.__strip_id_tag(it if it.find('-') == -1 else it[0:it.find('-')]), split_data))
                    for player_id in player_ids:
                        await __refresh_player_message(client, player_id)
                    await message.add_reaction('🪙')
                else:
                    await message.add_reaction('❌')
            if keywords[1] == "addplayer":
                player_data_list = keywords[2].split(',')
                player_id = utils.__strip_id_tag(player_data_list[0])
                player_data_list.pop(0)
                characters.add_player(player_id, player_data_list)
                players_channel = client.get_channel(firebase.get_character_info_channel_id())
                await players_channel.send(characters.get_up_to_date_player_message(player_id))
            if keywords[1] == "addcharacter":
                data_list = keywords[2].split(',')
                player_id = utils.__strip_id_tag(data_list[0])
                data_list.pop(0)
                characters.add_character(player_id, data_list)
                await __refresh_player_message(client, player_id)


def is_admin(message) -> bool:
    return message.author.guild_permissions.administrator
