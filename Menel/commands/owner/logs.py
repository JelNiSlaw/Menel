import time

import discord

from ... import logpath
from ...objects import Category, Command, Message


COMMAND = Command(
    'logs',
    syntax=None,
    description='Wysyła logi.',
    category=Category.OWNER,
    global_perms=5,
    hidden=True
)


def setup(cliffs):
    @cliffs.command('logs [here]:here', command=COMMAND)
    async def command(m: Message, here):
        dest = m.channel if here else m.author.dm_channel or await m.author.create_dm()

        with open(logpath, mode='rb') as f:
            await m.send(file=discord.File(f, f'{time.time_ns()}.log'), channel=dest, reply=False)