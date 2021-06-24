import discord

from .formatting import bold
from .text_tools import clean_content


class Confirm(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=10)
        self.user = user
        self.result = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message(
                f'Tylko {bold(clean_content(str(self.user)))} może używać tych przycisków', ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label='Potwierdź', style=discord.ButtonStyle.green)
    async def confirm(self, *_) -> None:
        self.result = True
        self.stop()

    @discord.ui.button(label='Anuluj')
    async def cancel(self, *_) -> None:
        self.result = False
        self.stop()