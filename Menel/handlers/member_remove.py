import discord

from ..objects.bot import Menel


def setup(bot: Menel):
    @bot.event
    async def on_member_remove(member: discord.Member):
        print(f'{member} left {member.guild}')