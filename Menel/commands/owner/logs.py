import time

import discord

from ...objects import Category, Command, Message
from ...setup import LOGPATH


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
        dest = m.channel if here else m.author

        await m.send(file=discord.File(LOGPATH, f'{time.time_ns()}.log'), channel=dest, reply=False)