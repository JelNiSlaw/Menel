import asyncio
from typing import Optional, Union

import discord

from ..objects.bot import bot
from ..resources.regexes import DISCORD_ID, USER_MENTION


async def get_user(
        search: str,
        guild: Optional[discord.Guild] = None,
        force_member: bool = False,
        force_fetch: bool = False
) -> Optional[Union[discord.Member, discord.User]]:
    if force_member and not guild:
        raise ValueError

    if len(search) < 3:
        return None

    if match := DISCORD_ID.fullmatch(search):
        user_id = int(match.group())
    elif match := USER_MENTION.fullmatch(search):
        user_id = int(match.group('ID'))
    else:
        user_id = None

    if guild:
        if user_id:
            if not force_fetch:
                if member := guild.get_member(user_id):
                    return member

            try:
                return await guild.fetch_member(user_id)
            except discord.HTTPException:
                pass

        if not force_fetch:
            if member := guild.get_member_named(search):
                return member

        try:
            members = await guild.query_members(query=search)
        except asyncio.TimeoutError:
            pass
        else:
            if members:
                return members[0]

    if user_id and not force_member:
        if not force_fetch:
            if user := bot.get_user(user_id):
                return user

        try:
            return await bot.fetch_user(user_id)
        except discord.HTTPException:
            pass