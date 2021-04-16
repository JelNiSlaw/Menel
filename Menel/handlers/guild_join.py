import logging

import discord

from ..objects import Menel


log = logging.getLogger(__name__)


def setup(bot: Menel):
    @bot.event
    async def on_guild_join(guild: discord.Guild):
        log.info(f'Joined server {guild}')