from datetime import datetime

import discord

from ..objects.bot import Menel
from ..objects.cooldowns import cooldowns
from ..objects.database import database


def setup(bot: Menel):
    @bot.event
    async def on_member_update(before: discord.Member, after: discord.Member):
        if after.bot or before.status == after.status:
            return

        if not cooldowns.auto(after.id, '_status', 1, include_owner=True):
            if after.status != discord.Status.offline:
                source = after
            else:
                source = before

            desktop = source.desktop_status != discord.Status.offline
            web = source.web_status != discord.Status.offline
            mobile = source.mobile_status != discord.Status.offline

            await database.lastseen.replace_one(
                {'_id': after.id},
                {
                    'status': source.status.value,
                    'devices': (desktop, web, mobile),
                    'time': datetime.utcnow()
                },
                upsert=True
            )