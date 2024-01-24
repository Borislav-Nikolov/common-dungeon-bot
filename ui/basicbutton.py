from discord.ui import Button
from typing import Callable, Awaitable
from discord.interactions import Interaction


class BasicButton(Button):
    def __init__(self, label, style, on_click: Callable[[Interaction], Awaitable]):
        super().__init__(label=label, style=style)
        self.on_click = on_click

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        await self.on_click(interaction)
