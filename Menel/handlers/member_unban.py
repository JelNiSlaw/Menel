import discord

from ..objects.bot import Menel


def setup(bot: Menel):
    @bot.event
    async def on_member_unban(guild: discord.Guild, user: discord.User):
        print(f'{user} was unbanned from {guild}')