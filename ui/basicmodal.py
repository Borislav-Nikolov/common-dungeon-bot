from discord.ui import Modal, TextInput
from typing import Callable, Awaitable, Optional
from discord.interactions import Interaction


class BasicModal(Modal):
    def __init__(
            self,
            title: str,
            input_label: str,
            on_submit_callback: Callable[[Interaction, str], Awaitable],
            input_placeholder: Optional[str] = None
    ):
        super().__init__(title=title)
        self.input_label = input_label
        self.on_submit_callback = on_submit_callback
        self.levels_input = TextInput(label=input_label, min_length=1, placeholder=input_placeholder)
        self.add_item(self.levels_input)

    async def on_submit(self, interaction: Interaction):
        await self.on_submit_callback(interaction, self.levels_input.value)
