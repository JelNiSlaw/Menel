import asyncio
from io import BytesIO
from urllib import parse

import aiohttp
import discord

from ...functions import clean_content
from ...objects import Category, Command, Message


COMMAND = Command(
    'minecraft',
    syntax=None,
    description='Pokazuje skin wybranego gracza.',
    aliases=('mc', 'skin'),
    category=Category.UTILS,
    cooldown=3
)


def setup(cliffs):
    @cliffs.command('(minecraft|mc|skin) <player...>', command=COMMAND)
    async def command(m: Message, player):
        async with m.channel.typing():
            async with aiohttp.request(
                    'GET', f'https://api.mojang.com/users/profiles/minecraft/{parse.quote(player)}',
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 204:
                    await m.error('Nie znalazłem gracza o tym nicku.')
                    return

                json = await r.json()

            uuid = json['id']
            name = json['name']

            name_history, avatar, head, body = await asyncio.gather(
                get_name_history(uuid), get_avatar(uuid), get_head(uuid), get_body(uuid)
            )

            avatar = discord.File(BytesIO(avatar), 'avatar.png')
            head = discord.File(BytesIO(head), 'head.png')
            body = discord.File(BytesIO(body), 'body.png')

            embed = discord.Embed(
                description=f'Historia nazw: {name_history}\n'
                            f'UUID: `{uuid}`'
            )
            embed.set_author(name=name, icon_url='attachment://head.png')
            embed.set_thumbnail(url='attachment://avatar.png')
            embed.set_image(url='attachment://body.png')

        await m.send(embed=embed, files=[avatar, head, body])


async def get_name_history(uuid: str) -> str:
    async with aiohttp.request(
            'GET', f'https://api.mojang.com/user/profiles/{parse.quote(uuid)}/names',
            timeout=aiohttp.ClientTimeout(total=10)
    ) as r:
        json = await r.json()
        return ', '.join(clean_content(name['name']) for name in json)


async def get_avatar(uuid: str) -> bytes:
    async with aiohttp.request(
            'GET', f'https://crafatar.com/avatars/{parse.quote(uuid)}?size=256&overlay',
            timeout=aiohttp.ClientTimeout(total=10)
    ) as r:
        return await r.read()


async def get_head(uuid: str) -> bytes:
    async with aiohttp.request(
            'GET', f'https://crafatar.com/renders/head/{parse.quote(uuid)}?scale=6&overlay',
            timeout=aiohttp.ClientTimeout(total=10)
    ) as r:
        return await r.read()


async def get_body(uuid: str) -> bytes:
    async with aiohttp.request(
            'GET', f'https://crafatar.com/renders/body/{parse.quote(uuid)}?scale=10&overlay',
            timeout=aiohttp.ClientTimeout(total=10)
    ) as r:
        return await r.read()