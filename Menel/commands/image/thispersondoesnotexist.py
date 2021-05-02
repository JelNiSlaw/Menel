import mimetypes
from io import BytesIO

import aiohttp
import discord

from ...objects import Category, Command, Message


COMMAND = Command(
    'thispersondoesnotexist',
    syntax=None,
    description='Wysyła twarz wygenerowaną przez thispersondoesnotexist.com.',
    aliases=('this-person-does-not-exist', 'tpdne', 'person'),
    category=Category.IMAGE,
    cooldown=3
)


def setup(cliffs):
    @cliffs.command('thispersondoesnotexist|this-person-does-not-exist|tpdne|person', command=COMMAND)
    async def command(m: Message):
        async with m.channel.typing():
            async with aiohttp.request(
                    'GET', 'https://thispersondoesnotexist.com/image',
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                ext = mimetypes.guess_extension(r.content_type, strict=False) or '.jpg'
                await m.send(file=discord.File(BytesIO(await r.read()), filename='image' + ext))