import asyncio
from util import utils, botutils, itemutils
from controller import homebrew


# TODO: Needs serious revision and finishing.
async def handle_homebrew_commands(message, client):
    homebrew_key = '$homebrew'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    # `False` because temporarily disabled
    if False and keywords[0] == homebrew_key and botutils.is_admin(message):
        if keywords[1] == 'item':
            new_item = dict()
            new_item[itemutils.ITEM_FIELD_OFFICIAL] = False

            def check_author(checked_message):
                return checked_message.author.id == message.author.id

            # TODO: apply function to the rest of the prompts
            # Input item name
            await item_creation_prompt(
                client=client,
                message=message,
                bot_message="Input item **name**.\n```yaml\nMax 48 symbols.\n```",
                error_message="Item name is too long. Try again.",
                timeout=60.0,
                new_item=new_item,
                new_item_parameter=itemutils.ITEM_FIELD_NAME,
                check_input=lambda name: len(name) <= 48,
                produce_result=lambda name: name
            )

            can_continue = False

            # Input item description
            def check_item_description(description):
                return len(description) <= 2048
            while not can_continue:
                await message.author.send("Input item **description**.\n```yaml\nMax 1024 symbols.\n```")
                item_creator_reply = await client.wait_for('message', timeout=300.0, check=check_author)
                can_continue = check_item_description(item_creator_reply.content)
                if not can_continue:
                    await message.author.send("Description is too long. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_DESCRIPTION] = item_creator_reply.content
            can_continue = False

            # Input item rarity
            def check_item_rarity_input(rarity):
                try:
                    utils.rarity_to_ordinal(rarity)
                except ValueError:
                    return False
                return True
            while not can_continue:
                await message.author.send(
                    "Input item **rarity**.\n```yaml\n"
                    "Possible values: common, uncommon, rare, very rare, legendary\n```")
                item_creator_reply = await client.wait_for('message', timeout=120.0, check=check_author)
                can_continue = check_item_rarity_input(item_creator_reply.content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_RARITY] = item_creator_reply.content.capitalize()
            can_continue = False

            # Input item rarity level
            def check_item_rarity_level_input(rarity_level):
                lowered_rarity_level = rarity_level.lower()
                return lowered_rarity_level == "minor" or lowered_rarity_level == "major"
            while not can_continue:
                await message.author.send("Input item **rarity level**.\n```yaml\nPossible values: minor, major\n```")
                item_creator_reply = await client.wait_for('message', timeout=120.0, check=check_author)
                can_continue = check_item_rarity_level_input(item_creator_reply.content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_RARITY_LEVEL] = item_creator_reply.content.upper()
            can_continue = False

            # It item consumable
            def check_item_consumable(consumable):
                lowered_consumable = consumable.lower()
                return lowered_consumable == "yes" or lowered_consumable == "no"
            while not can_continue:
                await message.author.send("Is item **consumable**?\n```yaml\nPossible values: Yes, No\n```")
                item_creator_reply = await client.wait_for('message', timeout=60.0, check=check_author)
                lowered_content = item_creator_reply.content.lower()
                can_continue = check_item_consumable(lowered_content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_CONSUMABLE] = True if lowered_content == "yes" else False
            can_continue = False

            # Is item attunable
            def check_item_attunable(attunable):
                lowered_attunable = attunable.lower()
                return lowered_attunable == "yes" or lowered_attunable == "no"
            while not can_continue:
                await message.author.send("Is item **attunable**?\n```yaml\nPossible values: Yes, No\n```")
                item_creator_reply = await client.wait_for('message', timeout=60.0, check=check_author)
                lowered_content = item_creator_reply.content.lower()
                can_continue = check_item_attunable(lowered_content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_ATTUNEMENT] = True if lowered_content == "yes" else False
            can_continue = False

            # Is item banned from the Magic Shop
            def check_item_banned(banned):
                lowered_banned = banned.lower()
                return lowered_banned == "yes" or lowered_banned == "no"
            while not can_continue:
                await message.author.send(
                    "Is item **banned** from the Magic Shop?\n```yaml\nPossible values: Yes, No\n```")
                item_creator_reply = await client.wait_for('message', timeout=60.0, check=check_author)
                lowered_content = item_creator_reply.content.lower()
                can_continue = check_item_banned(lowered_content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    new_item[itemutils.ITEM_FIELD_BANNED] = True if lowered_content == "yes" else False
            can_continue = False

            # Confirm item creation
            confirmed = False

            def check_confirmation(confirmation):
                lowered_confirmation = confirmation.lower()
                return lowered_confirmation == "yes" or lowered_confirmation == "no"
            while not can_continue:
                await message.author.send(
                    "Confirm creation of item:\n" +
                    itemutils.get_homebrew_item_confirmation_description(new_item) +
                    "```yaml\nPossible values: Yes, No\n```")
                item_creator_reply = await client.wait_for('message', timeout=300.0, check=check_author)
                lowered_content = item_creator_reply.content.lower()
                can_continue = check_confirmation(lowered_content)
                if not can_continue:
                    await message.author.send("Wrong input. Try again.")
                else:
                    confirmed = True if lowered_content == "yes" else False

            if confirmed:
                homebrew.save_new_item(new_item)
                await message.author.send(f'**{new_item[itemutils.ITEM_FIELD_NAME]}** was created.')
            else:
                await message.author.send(f'**{new_item[itemutils.ITEM_FIELD_NAME]}** was NOT created.')


async def item_creation_prompt(
        client,
        message,
        bot_message: str,
        error_message: str,
        timeout,
        new_item: dict,
        new_item_parameter: str,
        check_input,
        produce_result
):

    can_continue = False

    def check_author(checked_message):
        return checked_message.author.id == message.author.id

    try:
        while not can_continue:
            await message.author.send(bot_message)
            item_creator_reply = await client.wait_for('message', timeout=timeout, check=check_author)
            lowered_content = item_creator_reply.content.lower()
            can_continue = check_input(lowered_content)
            if not can_continue:
                await message.author.send(error_message)
            else:
                new_item[new_item_parameter] = produce_result(lowered_content)
    except asyncio.TimeoutError:
        await message.author.send("Item creation timed out.")
        raise Exception()
