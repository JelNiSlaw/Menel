import asyncio
from typing import Callable, Literal, Optional, Union

import discord
from discord.ext import commands

from ..bot import Menel
from ..utils.context import Context
from ..utils.converters import ClampedNumber
from ..utils.misc import chunk
from ..utils.text_tools import plural, plural_time
from ..utils.views import Confirm


class PurgeFilters(commands.FlagConverter, case_insensitive=True, prefix="--", delimiter=""):
    before: Optional[discord.Object]
    after: Optional[discord.Object]
    contains: Optional[str]
    users: Optional[tuple[discord.User]] = commands.flag(aliases=["user"])
    mentions: Optional[tuple[discord.User]]
    type: Optional[Literal["humans", "bots", "commands", "webhooks", "system"]]


def checks_from_filters(filters: PurgeFilters) -> list[Callable]:
    checks = []
    if filters.contains is not None:
        contains = filters.contains.lower()
        checks.append(lambda msg: contains in msg.content.lower())

    if filters.users is not None:
        users = set(filters.users)
        checks.append(lambda msg: msg.author in users)

    if filters.mentions is not None:
        mentions = set(filters.mentions)
        empty_set = set()
        checks.append(lambda msg: set(msg.mentions) & mentions != empty_set)

    if filters.type is not None:
        msg_type = filters.type
        if msg_type == "humans":
            checks.append(lambda msg: not msg.author.bot)
        elif msg_type == "bots":
            checks.append(lambda msg: msg.author.bot)
        elif msg_type == "commands":
            command = discord.MessageType.application_command
            checks.append(lambda msg: msg.type is command)
        elif msg_type == "webhooks":
            checks.append(lambda msg: msg.webhook_id is not None)
        elif msg_type == "system":
            types = {discord.MessageType.default, discord.MessageType.reply, discord.MessageType.application_command}
            checks.append(lambda msg: msg.type not in types)
    return checks


class Moderation(commands.Cog):
    @commands.command(aliases=["clear", "clean"], ignore_extra=False)
    @commands.has_permissions(read_message_history=True, manage_messages=True)
    @commands.bot_has_permissions(read_message_history=True, manage_messages=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.max_concurrency(2, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel, wait=True)
    async def purge(self, ctx: Context, limit: ClampedNumber(1, 1000), *, filters: PurgeFilters):
        """Usuwa określoną ilość wiadomośi spełniających wszystkie filtry"""
        async with ctx.typing():
            checks = checks_from_filters(filters)
            to_delete = []
            async for m in ctx.channel.history(
                limit=limit * 5, before=filters.before, after=filters.after, oldest_first=False
            ):
                if all(check(m) for check in checks):
                    to_delete.append(m)
                    if len(to_delete) > limit:
                        break

        if not to_delete:
            await ctx.error("Nie znaleziono żadnych wiadomości pasującej do filtrów")
            return

        if ctx.message not in to_delete:
            to_delete.insert(0, ctx.message)
        del to_delete[limit + 1 :]

        count_str = plural(len(to_delete) - 1, "wiadomość", "wiadomości", "wiadomości")

        view = Confirm(ctx.author)
        m = await ctx.embed(f"Na pewno chcesz usunąć {count_str}?", view=view)
        await view.wait()
        await m.delete()
        if view.result is not True:
            await ctx.embed("Anulowano usuwanie wiadomości", no_reply=True)
            return

        for messages in chunk(to_delete, 100):
            await ctx.channel.delete_messages(messages)
            if len(messages) >= 100:
                await asyncio.sleep(1)

        await ctx.embed(f"Usunięto {count_str}", no_reply=True, delete_after=5)

    @commands.command("toggle-nsfw", aliases=["mark_nsfw", "nsfw"])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def toggle_nsfw(self, ctx: Context, *, channel: discord.TextChannel = None):
        """Oznacza lub odznacza wybrany kanał jako NSFW"""
        channel = channel or ctx.channel
        before = channel.nsfw
        await channel.edit(nsfw=not before)
        await ctx.embed(f"Oznaczono {channel.mention} jako {'SFW' if before else 'NSFW'}")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(2, 5, commands.BucketType.channel)
    async def slowmode(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel],
        *,
        time: Union[Literal[False], ClampedNumber(1, 21600)],
    ):
        """Ustawia czas slowmode kanału"""
        channel = channel or ctx.channel
        await channel.edit(slowmode_delay=time)
        if time is not False:
            await ctx.embed(f"Ustawiono czas slowmode na {channel.mention} na {plural_time(time)}")
        else:
            await ctx.embed(f"Wyłączono slowmode na {channel.mention}")


def setup(bot: Menel):
    bot.add_cog(Moderation())
