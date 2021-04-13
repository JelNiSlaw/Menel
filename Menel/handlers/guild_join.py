import discord

from .. import log
from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_guild_join(guild: discord.Guild):
        log.info(f'Joined server {guild}')