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
            on_submit_callback: Callable[[Interaction, str, str], Awaitable]
    ):
        super().__init__(timeout=None)
        self.on_submit_callback = on_submit_callback

        async def on_status_select(interaction: Interaction, status: str):
            return await interaction.response.defer()

        self.status_selection = StatusSelect(on_submit_callback=on_status_select)

        async def on_submit(interaction: Interaction, character_name: str):
            return await self.on_submit_callback(
                # TODO: test if self.status_selection.values doesn't somehow select something that was selected from another user
                interaction, character_name, self.status_selection.values[0]
            )

        async def button_click(button_interaction: Interaction):
            if len(self.status_selection.values) > 0:
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
