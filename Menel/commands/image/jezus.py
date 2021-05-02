import imghdr
from io import BytesIO
from os import getenv

import aiohttp
import discord

from ...objects import Category, Command, Message


COMMAND = Command(
    'jezus',
    syntax=None,
    description='Wysyła losowe zdjęcie Jezusa.',
    aliases=('jesus',),
    category=Category.IMAGE,
    cooldown=3
)


def setup(cliffs):
    @cliffs.command('jezus|jesus', command=COMMAND)
    async def command(m: Message):
        async with m.channel.typing():
            async with aiohttp.request(
                    'GET', 'https://obrazium.com/v1/jesus',
                    headers={'Authorization': getenv('OBRAZIUM_TOKEN')},
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 200:
                    file = BytesIO(await r.read())
                    ext = imghdr.what(file) or 'jpeg'
                    await m.send(file=discord.File(file, filename='jezus.' + ext))
                else:
                    await m.error('Nie działa')