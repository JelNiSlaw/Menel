import asyncio
from typing import Optional, Type, Union

import discord

from ..objects.bot import bot
from ..resources.regexes import USER_MENTION


async def get_user(
        search: str,
        guild: Optional[discord.Guild] = None,
        force_type: Optional[Type[Union[discord.User, discord.Member]]] = None
) -> Optional[Union[discord.Member, discord.User]]:
    if force_type == discord.User and guild:
        raise ValueError

    if len(search) < 3:
        return None

    if search.isdigit() and len(search) == 18:
        user_id = int(search)
    elif match := USER_MENTION.fullmatch(search):
        user_id = int(match.group('ID'))
    else:
        user_id = None

    if guild:
        if user_id:
            if member := guild.get_member(user_id):
                return member

            try:
                return await guild.fetch_member(user_id)
            except discord.HTTPException:
                pass

        if member := guild.get_member_named(search):
            return member

        try:
            members = await guild.query_members(query=search)
        except asyncio.TimeoutError:
            return None

        if members:
            return members[0]

    if user_id and not force_type == discord.Member:
        if user := bot.get_user(user_id):
            return user

        try:
            return await bot.fetch_user(user_id)
        except discord.HTTPException:
            pass