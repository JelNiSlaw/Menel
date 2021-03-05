import discord

from ..command_dispatcher import dispatch
from ..functions import clean_content, code, constant_length_text as const_len, cut_long_text
from ..modules import autoresponders
from ..objects import Menel, Message, cooldowns
from ..resources import regexes


def setup(bot: Menel):
    @bot.event
    async def on_message(m: discord.Message):
        m = Message(m)

        if m.content:
            print(
                f'{const_len(str(m.guild), 16)} {const_len(str(m.channel), 16)} {const_len(str(m.author), 16)} '
                f'{cut_long_text(m.clean_content, 128, 1)}'
            )

        if m.author.bot or not m.guild or not m.channel.permissions_for(m.guild.me).send_messages:
            return

        prefix = '.'

        if regexes.mention(bot.user.id).fullmatch(m.content):
            if not cooldowns.auto(m.author.id, '_mention', 3):
                await m.send(f'Cześć! Mój prefix to {code(clean_content(prefix))}')

        elif m.content.lower().startswith(prefix):
            await dispatch(m.content[len(prefix):], m, prefix)

        elif match := regexes.mention(bot.user.id).match(m.content):
            await dispatch(m.content[len(match.group()):], m, f'@{bot.user.name}')

        else:
            await autoresponders.respond(m)