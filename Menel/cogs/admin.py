import time
from typing import Literal

import discord
from discord.ext import commands

from Menel.utils.logs import LOGPATH
from ..objects.context import Context


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not await ctx.bot.is_owner(ctx.author):
            return False
        return True

    @commands.command(aliases=['r'])
    async def reload(self, ctx: Context):
        self.bot.reload_extensions()
        await ctx.react_or_send('\N{OK HAND SIGN}')

    @commands.command('clear-cache', aliases=['cc'])
    async def clear_cache(self, ctx: Context):
        self.bot.clear()
        await ctx.react_or_send('\N{OK HAND SIGN}')

    @commands.command(aliases=['stop', 's'])
    async def shutdown(self, ctx: Context):
        await ctx.react_or_send('\N{WAVING HAND SIGN}')
        await self.bot.close()

    @commands.command(aliases=['del'])
    async def delete(self, ctx: Context, *, message: discord.PartialMessage):
        await message.delete()
        await ctx.react_or_send('\N{OK HAND SIGN}')

    @commands.command()
    async def logs(self, ctx: Context, *, here: Literal['here'] = None):
        destination = ctx.channel if here is not None else ctx.author
        await ctx.send(file=discord.File(LOGPATH, f'{time.time_ns()}.log'), channel=destination, reply=False)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        wastebasket = '\N{WASTEBASKET}\N{VARIATION SELECTOR-16}'
        if await self.bot.is_owner(discord.Object(payload.user_id)) and payload.emoji.name == wastebasket:
            await self.bot.http.delete_message(payload.channel_id, payload.message_id)


def setup(bot):
    bot.add_cog(Admin(bot))