import discord

from ..objects.bot import Menel


def setup(bot: Menel):
    @bot.event
    async def on_message_edit(before: discord.Message, after: discord.Message):
        if not before.content:
            return

        if before.content == after.content:
            return

        from ..objects.snipes import snipes

        if not after.author.bot:
            snipes = snipes.edit
        else:
            snipes = snipes.botedit

        snipes[after.channel.id] = (before, after.edited_at)