from discord.ui import View
from ui.basicbutton import BasicButton
from discord.interactions import Interaction
from discord import ButtonStyle
from typing import Callable, Awaitable


class PlayerView(View):
    def __init__(
            self,
            on_view_details_click: Callable[[Interaction], Awaitable]
    ):
        super().__init__(timeout=None)
        self.add_item(
            BasicButton(
                label='View details',
                style=ButtonStyle.primary,
                on_click=on_view_details_click
            )
        )
