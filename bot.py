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
                firebase.set_shop_message_id(message.id)
            elif content.startswith('<@'):
                firebase.set_player_message_id(utils.strip_id_tag(content), message.id)
            return

        username = str(message.author.id)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        if user_message.startswith('$'):
            await handle_server_initialization_prompts(message)
            await handle_shop_commands(message, client)
            await handle_character_commands(message, client)

    client.run(bot_token)


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
    keywords = utils.split_strip(str(message.content), '.')
    if keywords[0] == shop_key and message.channel.id == firebase.get_shop_channel_id():
        command_message = keywords[1]
        if command_message == 'generate' and is_admin(message):
            character_levels_csv = keywords[2]
            await message.channel.send(magicshop.generate_new_magic_shop(character_levels_csv))
        elif command_message == 'refresh' and is_admin(message):
            shop_message = await message.channel.fetch_message(firebase.get_shop_message_id())
            await shop_message.edit(content=magicshop.get_current_shop_string())
        elif command_message.isnumeric():
            shop_message = await message.channel.fetch_message(firebase.get_shop_message_id())
            sold = magicshop.sell_item(message.author.id, int(command_message))
            if sold:
                shop_string = magicshop.get_current_shop_string()
                await shop_message.edit(content=shop_string)
                await refresh_player_message(client, message.author.id)
                await message.add_reaction('🪙')
            else:
                await message.add_reaction('❌')
        elif command_message == 'sell':
            # expected: rarity,rarity level
            rarity_data = utils.split_strip(keywords[2], ',')
            sold = magicshop.refund_item(message.author.id, rarity_data[0], rarity_data[1])
            if sold:
                await refresh_player_message(client, message.author.id)
                await message.add_reaction('🪙')
            else:
                await message.add_reaction('❌')


async def refresh_player_message(client, player_id):
    await update_player_message(client, player_id, characters.get_up_to_date_player_message(player_id))


async def update_player_message(client, player_id, new_message):
    players_channel = client.get_channel(firebase.get_character_info_channel_id())
    player_message_id = firebase.get_player_message_id(player_id)
    player_message = await players_channel.fetch_message(player_message_id)
    await player_message.edit(content=new_message)


async def handle_character_commands(message, client):
    characters_key = '$characters'
    keywords = utils.split_strip(str(message.content), '.')
    if keywords[0] == characters_key and is_admin(message):
        if keywords[1] == "hardinit":
            player_id = utils.strip_id_tag(keywords[2])
            characters.hardinit_player(player_id, keywords[3])
            players_channel = client.get_channel(firebase.get_character_info_channel_id())
            await players_channel.send(characters.get_up_to_date_player_message(player_id))
        elif message.channel.id == firebase.get_character_info_channel_id():
            if keywords[1] == "addsession":
                if characters.add_session(keywords[2]):
                    split_data = utils.split_strip(keywords[2], ',')
                    player_ids = list(
                        map(lambda it: utils.strip_id_tag(it if it.find('-') == -1 else it[0:it.find('-')]), split_data))
                    for player_id in player_ids:
                        await refresh_player_message(client, player_id)
                    await message.add_reaction('🪙')
                else:
                    await message.add_reaction('❌')
            elif keywords[1] == "addplayer":
                player_data_list = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_data_list[0])
                player_data_list.pop(0)
                characters.add_player(player_id, player_data_list)
                players_channel = client.get_channel(firebase.get_character_info_channel_id())
                await players_channel.send(characters.get_up_to_date_player_message(player_id))
            elif keywords[1] == "addcharacter":
                data_list = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(data_list[0])
                data_list.pop(0)
                characters.add_character(player_id, data_list)
                await refresh_player_message(client, player_id)
            elif keywords[1] == "deletecharacter":
                player_id_to_character_name = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_id_to_character_name[0])
                characters.delete_character(player_id, player_id_to_character_name[1])
                await refresh_player_message(client, player_id)
            elif keywords[1] == "changename":
                player_id_and_names = utils.split_strip(keywords[2], ',')
                player_id = utils.strip_id_tag(player_id_and_names[0])
                characters.change_character_name(player_id, player_id_and_names[1], player_id_and_names[2])
                await refresh_player_message(client, player_id)


def is_admin(message) -> bool:
    return message.author.guild_permissions.administrator
