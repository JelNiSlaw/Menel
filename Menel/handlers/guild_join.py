import discord

from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_guild_join(guild: discord.Guild):
        print(f'Joined server {guild}')