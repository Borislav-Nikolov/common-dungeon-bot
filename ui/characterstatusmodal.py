from discord.ui import TextInput, Select, View, Modal
from discord import ButtonStyle
from discord.components import SelectOption
from typing import Callable, Awaitable, Optional
from discord.interactions import Interaction
from util import charactersutils
from ui.basicbutton import BasicButton
from ui.basicmodal import BasicModal


class CharacterStatusView(View):
    def __init__(
            self,
            on_submit_callback: Callable[[Interaction, str, str], Awaitable[bool]],
            on_handle_error: Callable[[Interaction], Awaitable]
    ):
        super().__init__(timeout=None)
        self.on_submit_callback = on_submit_callback
        self.on_handle_error = on_handle_error

        status_selection_per_user = dict()

        async def on_status_select(interaction: Interaction, status: str):
            print(f'onstatusselect: user_id={interaction.user.id}, status: {status}')
            status_selection_per_user[interaction.user.id] = status
            return await interaction.response.defer()

        self.status_selection = StatusSelect(on_submit_callback=on_status_select)

        async def on_submit(interaction: Interaction, character_name: str):
            print(f'onsubmit: user_id={interaction.user.id}, character_name={character_name}, from dict={status_selection_per_user[interaction.user.id]}')
            if interaction.user.id in status_selection_per_user and len(
                    status_selection_per_user[interaction.user.id]) > 0:
                new_status = status_selection_per_user.pop(interaction.user.id, None)
                print(f'new status extracted = {interaction.user.id in status_selection_per_user}')
                if new_status is None:
                    return await self.on_handle_error(interaction)
                if not await self.on_submit_callback(interaction, character_name, new_status):
                    # reinitialize the value as it could not be used
                    if len(self.status_selection.values) > 0:
                        status_selection_per_user[interaction.user.id] = self.status_selection.values[0]
            else:
                return await self.on_handle_error(interaction)

        async def button_click(button_interaction: Interaction):
            if button_interaction.user.id in status_selection_per_user and len(
                    status_selection_per_user[button_interaction.user.id]) > 0:
                print(f'button_click: user_id={button_interaction.user.id}, from dict={status_selection_per_user[button_interaction.user.id]}')
                return await button_interaction.response.send_modal(
                    BasicModal(
                        title='Character status change',
                        input_label='Character name',
                        input_placeholder='Character name...',
                        on_submit_callback=on_submit
                    )
                )
            return await button_interaction.response.defer()

        self.button = BasicButton(
            label='Change character status',
            style=ButtonStyle.primary,
            on_click=button_click
        )
        self.add_item(self.status_selection)
        self.add_item(self.button)


class StatusSelect(Select):

    def __init__(self, on_submit_callback: Callable[[Interaction, str], Awaitable]):
        super().__init__(
            placeholder='Choose a new status',
            min_values=1,
            max_values=1,
            options=list(
                map(lambda status_key: SelectOption(
                    label=charactersutils.status_label(status_key),
                    value=status_key,
                    description=charactersutils.status_description(status_key),
                    emoji=charactersutils.status_emoji(status_key)
                ), charactersutils.VALID_CHARACTER_STATUSES)
            )
        )
        self.on_submit_callback = on_submit_callback

    async def callback(self, interaction: Interaction):
        return await self.on_submit_callback(interaction, self.values[0])
