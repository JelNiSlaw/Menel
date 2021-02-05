import discord

from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_member_join(member: discord.Member):
        print(f'{member} joined {member.guild}')