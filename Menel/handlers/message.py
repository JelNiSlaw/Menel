import re

import discord

from ..command_dispatcher.dispatch import dispatch
from ..functions.constant_length_text import constant_length_text as clt
from ..functions.cut_long_text import cut_long_text
from ..objects.bot import Menel
from ..objects.cooldowns import cooldowns
from ..objects.message import Message
from ..resources import regexes
from ..setup.setup_cliffs import cliffs


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
            await dispatch(cliffs, m, prefix)

        elif re.match(regexes.mention(bot.user.id), m.content):
            await dispatch(cliffs, m, f'@{bot.user.name}')