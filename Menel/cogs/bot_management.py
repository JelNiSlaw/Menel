import time
from typing import Literal

import discord
from discord.ext import commands

from ..bot import Menel
from ..utils.context import Context
from ..utils.logs import LOGPATH


class BotManagement(commands.Cog, name='Bot Management', command_attrs={'hidden': True}):
    def __init__(self, bot: Menel):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(aliases=['r'])
    async def reload(self, ctx: Context):
        """Przeładowuje rozszerzenia bota"""
        self.bot.reload_extensions()
        await ctx.react_or_send('\N{OK HAND SIGN}')

    @commands.command(aliases=['stop', 's'])
    async def shutdown(self, ctx: Context):
        """Zamyka połączenie z Discordem i wyłącza bota"""
        await ctx.ok_hand()
        await self.bot.close()

    @commands.command(aliases=['del'])
    async def delete(self, ctx: Context, *, message: discord.PartialMessage):
        """
        Usuwa wiadomość
        `message`: ID lub link wiadomości
        """
        await message.delete()
        await ctx.react_or_send('\N{OK HAND SIGN}')

    @commands.command()
    async def logs(self, ctx: Context, *, here: Literal['here'] = None):
        """
        Wysyła plik z logami bota
        `here`: wysyła logi na obecnym kanale zamiast w wiadomości prywatnej
        """
        destination = ctx.channel if here is not None else ctx.author
        await ctx.send(file=discord.File(LOGPATH, f'{time.time_ns()}.log'), channel=destination, reply=False)

    @commands.command(aliases=['block'])
    async def blacklist(self, ctx: Context, *users: discord.Object):
        """Dodaje osoby do blacklisty"""
        await ctx.db.add_blacklist(*(user.id for user in users))
        await ctx.ok_hand()

    @commands.command(aliases=['unblock'])
    async def unblacklist(self, ctx: Context, *users: discord.Object):
        """Usuwa osoby z blacklisty"""
        await ctx.db.remove_blacklist(*(user.id for user in users))
        await ctx.ok_hand()

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        wastebasket = '\N{WASTEBASKET}\N{VARIATION SELECTOR-16}'
        if await self.bot.is_owner(discord.Object(payload.user_id)) and payload.emoji.name == wastebasket:
            await self.bot.http.delete_message(payload.channel_id, payload.message_id)


def setup(bot: Menel):
    bot.add_cog(BotManagement(bot))