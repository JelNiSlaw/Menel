import asyncio
import re

import aiohttp
import discord

from ...functions import clean_content, embed_with_author
from ...objects import Category, Command, Message


COMMAND = Command(
    'math',
    syntax=None,
    description='Oblicza działanie matematyczne.',
    aliases=('m', 'calculate', 'calculator', 'calc'),
    category=Category.UTILS,
    cooldown=2
)


def setup(cliffs):
    @cliffs.command('(math|m|calculate|calculator|calc) <expression...>', command=COMMAND)
    async def command(m: Message, expression):
        async with m.channel.typing():
            if re.sub(r'\s+', '', expression) == '2+2':
                result = '5'
                color = discord.Color.green()
                await asyncio.sleep(1)
            else:
                async with aiohttp.request(
                        'POST', 'https://api.mathjs.org/v4/',
                        json={'expr': expression},
                        timeout=aiohttp.ClientTimeout(total=10)
                ) as r:
                    json = await r.json()

                if not json['error']:
                    result = json['result']
                    color = discord.Colour.green()
                else:
                    result = json['error']
                    color = discord.Colour.red()

            embed = embed_with_author(
                m.author,
                discord.Embed(description=clean_content(result, max_length=2048, max_lines=8), colour=color)
            )
            embed.set_footer(text='Kalkulator Stanisław Jelnicki')

        await m.send(embed=embed)