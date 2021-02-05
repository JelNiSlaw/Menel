import asyncio

import discord
from cliffs import MismatchedLiteralSuggestion

from ..objects import bot, Message


async def redispatch(e: MismatchedLiteralSuggestion, m: Message, prefix: str, notice_msg: Message):
    def check(msg: discord.Message):
        return msg.author == m.author and msg.channel == m.channel


    try:
        message = await bot.wait_for('message', check=check, timeout=10)
    except asyncio.TimeoutError:
        try:
            await notice_msg.delete()
        except discord.HTTPException:
            pass
        return

    bot.loop.create_task(notice_msg.delete())

    if message.content.lower() not in ('tak', 'yes', 't', 'y'):
        return

    command = m.content[:e.actual.start] + e.expected.value + m.content[e.actual.end + 1:]
    m.created_at = message.created_at

    from ..command_dispatcher import dispatch

    await dispatch(command, m, prefix)