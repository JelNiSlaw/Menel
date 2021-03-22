import base64
from io import BytesIO

import discord

from ...objects import Category, Command, Message


COMMAND = Command(
    'base64encode',
    syntax=None,
    description='Koduje załączony plik do Base64.',
    category=Category.UTILS,
    cooldown=2
)


def setup(cliffs):
    @cliffs.command('base64encode', command=COMMAND)
    async def command(m: Message):
        if not m.attachments:
            await m.error('Załącz jakiś plik')
            return

        a = m.attachments[0]

        await m.send(
            file=discord.File(
                BytesIO(base64.b64encode(await a.read())),
                a.filename.rsplit('.', 1)[0] + '.txt'
            )
        )