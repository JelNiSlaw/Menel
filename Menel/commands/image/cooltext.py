from io import BytesIO

import aiohttp
import discord

from ...functions import embed_with_author
from ...objects import Category, Command, Message


COMMAND = Command(
    'cooltext',
    syntax=None,
    description='Wysyła palący się tekst ze strony cooltext.com.',
    aliases=('cooltext', 'burning', 'burning-text'),
    category=Category.IMAGE,
    cooldown=2
)


def setup(cliffs):
    @cliffs.command('(cooltext|burning|burning-text) <text...>', command=COMMAND)
    async def command(m: Message, text):
        async with aiohttp.request(
                'POST', 'https://cooltext.com/PostChange',
                data={
                    'LogoID': 3779758524,
                    'Text': text,
                    'FontSize': 70,
                    'Color1_color': '#FF0000',
                    'Integer1': 15,
                    'Boolean1': 'on',
                    'Integer13': 'on',
                    'Integer12': 'on',
                    'BackgroundColor_color': '#000000'
                },
                timeout=aiohttp.ClientTimeout(total=20)
        ) as r:
            file_url = (await r.json())['renderLocation']

        async with aiohttp.request('GET', file_url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            file = await r.read()

        embed = discord.Embed(colour=discord.Colour.orange())
        embed = embed_with_author(m.author, embed)
        embed.set_image(url='attachment://burning.gif')

        await m.send(embed=embed, file=discord.File(BytesIO(file), 'burning.gif'))