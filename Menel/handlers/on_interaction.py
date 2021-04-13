import discord

from .. import log
from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_interaction(interaction: discord.Interaction):
        log.debug(interaction.data)