from datetime import datetime

import discord

from ..objects import Menel, cooldowns, database


def setup(bot: Menel):
    @bot.event
    async def on_member_update(before: discord.Member, after: discord.Member):
        if before.status == after.status or after.status != discord.Status.offline:
            return

        if not cooldowns.auto(after.id, '_status', 1, include_owner=True):
            desktop = before.desktop_status != discord.Status.offline
            web = before.web_status != discord.Status.offline
            mobile = before.mobile_status != discord.Status.offline

            await database.lastseen.replace_one(
                {'_id': after.id},
                {
                    'status': before.status.value,
                    'devices': (desktop, web, mobile),
                    'time': datetime.utcnow()
                },
                upsert=True
            )