from discord.ui import TextInput, Select, View
from discord import ButtonStyle
from discord.components import SelectOption
from typing import Callable, Awaitable, Optional
from discord.interactions import Interaction
from util import charactersutils
from ui.basicbutton import BasicButton


class CharacterStatusView(View):
    def __init__(
            self,
            on_submit_callback: Callable[[Interaction, str, str], Awaitable]
    ):
        super().__init__(timeout=None)
        self.on_submit_callback = on_submit_callback
        self.character_name = TextInput(label='Character', min_length=1, placeholder='Character name...')
        options = list(
            map(lambda status_key: SelectOption(
                label=charactersutils.status_label(status_key),
                value=status_key,
                description=charactersutils.status_description(status_key),
                emoji=charactersutils.status_emoji(status_key)
            ), charactersutils.VALID_CHARACTER_STATUSES)
        )
        self.status_selection = Select(
            placeholder='Choose a new status',
            min_values=1,
            max_values=1,
            options=options
        )

        async def button_click(button_interaction: Interaction):
            return await self.on_submit_callback(
                button_interaction, self.character_name.value, self.status_selection.values[0])

        self.button = BasicButton(
            label='Change character status',
            style=ButtonStyle.primary,
            on_click=button_click
        )
        self.add_item(self.character_name)
        self.add_item(self.status_selection)
        self.add_item(self.button)
