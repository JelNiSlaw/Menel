import logging

import discord

from ..objects import Menel


log = logging.getLogger(__name__)


def setup(bot: Menel):
    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        wastebasket = '\N{WASTEBASKET}\N{VARIATION SELECTOR-16}'
        if bot.is_owner(payload.user_id) and payload.emoji.name == wastebasket:
            await bot.http.delete_message(payload.channel_id, payload.message_id)