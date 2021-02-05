from datetime import datetime

import discord

from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_message_delete(message: discord.Message):
        if not message.content:
            return

        from ..objects import snipes

        if not message.author.bot:
            snipes = snipes.delete
        else:
            snipes = snipes.botdelete

        snipes[message.channel.id] = (message, datetime.utcnow())