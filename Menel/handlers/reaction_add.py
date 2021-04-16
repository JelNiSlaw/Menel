import logging

import discord

from ..objects import Menel


log = logging.getLogger(__name__)


def setup(bot: Menel):
    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        if bot.is_owner(payload.user_id) and payload.emoji.name == '🗑️':
            try:
                message = await (await bot.fetch_channel(payload.channel_id)).fetch_message(payload.message_id)
                if message.author == bot.user:
                    await message.delete()
            except discord.HTTPException as e:
                log.warning(e)