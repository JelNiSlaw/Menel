import re

import discord

from ..command_dispatcher import dispatch
from ..functions import constant_length_text as clt, cut_long_text
from ..objects import cooldowns, Menel, Message
from ..resources import regexes


def setup(bot: Menel):
    @bot.event
    async def on_message(m: discord.Message):
        m = Message(m)

        if m.content:
            print(f'{clt(str(m.guild), 16)}\t{clt(str(m.channel), 16)}\t{clt(str(m.author), 16)}' +
                  ' -> ' + cut_long_text(m.clean_content, 128))

        if m.author.bot or not m.guild:
            return

        prefix = '.'

        if re.fullmatch(regexes.mention(bot.user.id), m.content):
            if not cooldowns.auto(m.author.id, '_mention', 3):
                await m.channel.send('Cześć')

        elif m.content.lower().startswith(prefix):
            await dispatch(m.content[len(prefix):], m, prefix)

        elif match := re.match(regexes.mention(bot.user.id), m.content):
            await dispatch(m.content[len(match.group())], m, f'@{bot.user.name}')