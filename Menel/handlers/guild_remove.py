import discord

from ..objects.bot import Menel


def setup(bot: Menel):
    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        print(f'Left server {guild}')