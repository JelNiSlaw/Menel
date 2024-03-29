from typing import Union

import discord

from .markdown import bold
from .text_tools import escape


class Confirm(discord.ui.View):
    def __init__(self, user: Union[discord.Member, discord.abc.User]):
        super().__init__(timeout=10)
        self.user = user
        self.result = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message(
                f"Tylko {bold(escape(str(self.user)))} może używać tych przycisków", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Potwierdź", style=discord.ButtonStyle.green)
    async def confirm(self, *_) -> None:
        self.result = True
        self.stop()

    @discord.ui.button(label="Anuluj")
    async def cancel(self, *_) -> None:
        self.result = False
        self.stop()
