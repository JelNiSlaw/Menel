import logging

import discord

from ..objects import Menel


log = logging.getLogger(__name__)


def setup(bot: Menel):
    @bot.event
    async def on_interaction(interaction: discord.Interaction):
        log.debug(interaction.data)