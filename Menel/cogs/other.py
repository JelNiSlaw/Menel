import io
import random
from os import environ
from typing import Optional

import discord
from discord.ext import commands

from ..bot import Menel
from ..utils import markdown
from ..utils.context import Context
from ..utils.converters import URL
from ..utils.misc import chunk
from ..utils.text_tools import escape


class PxseuFlags(commands.FlagConverter, case_insensitive=True):
    name: Optional[str]
    url: Optional[URL]
    message: Optional[str]


class Other(commands.Cog):
    @commands.command(aliases=['carpet'])
    async def dywan(self, ctx: Context, width: int = 15, length: int = 10):
        """
        Zapraszam, darmowy dywan
        `width`: szerokość dywanu
        `length`: długość dywanu
        """
        if width < 2 or length < 2:
            await ctx.error('Taki dywan byłby za mały, kasztanie')
            return

        if width > 25 or length > 100 or width * length > 1024 + 512:
            await ctx.error('Taki dywan byłby za szeroki, kasztanie!')
            return

        lines = [f"┃{''.join(random.choice('╱╲') for _ in range(width))}┃" for _ in range(length)]

        line = '━' * width
        lines.insert(0, f'┏{line}┓')
        lines.append(f'┗{line}┛')
        lines = markdown.codeblock('\n'.join(lines), escape=False)
        await ctx.embed(f'Proszę, oto Twój darmowy dywan\n{lines}')

    @commands.command(aliases=['px', 'pikseu'], ignore_extra=False, hidden=True)
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def pxseu(self, ctx: Context, *, flags: PxseuFlags):
        """
        Wysyła anonimową wiadomość do pxseu
        `flags`: dane do wysłania
        `name`: wyświetlana nazwa
        `url`: link do pliku w embedzie
        `message`: treść wysłanej wiadomości
        """
        if flags.url:
            url = flags.url
        elif ctx.message.attachments:
            url = ctx.message.attachments[0].url
        else:
            url = None

        r = await ctx.client.post(
            'https://api.pxseu.com/v2/sendMessage',
            json={'message': flags.message, 'name': flags.name, 'attachment': url, 'user': ctx.author.id},
            headers={'Authorization': 'Bearer ' + environ['PXSEU_MESSAGE_TOKEN']}
        )
        json = r.json()
        message = escape(json['message'])

        if r.status_code == 200:
            await ctx.embed(message)
        else:
            await ctx.error(f'{r.status_code}: {message}')

    @commands.command('lengthen-url', aliases=['lengthen'])
    async def lengthen_url(self, ctx: Context, *, url: URL):
        """Wydłuża zbyt krótki link"""
        if len(url) > 512:
            await ctx.error('Przekroczono maksymalną długość linku')
            return

        with ctx.channel.typing():
            r = await ctx.client.get(f"https://api.{'a' * 56}.com/a", params={'url': url})
            text = r.text

            if text == 'INVALID_URL':
                await ctx.error('Podano nieprawidłowy adres URL')
                return

        await ctx.send(text)

    @commands.command(aliases=['str-rot', 'rot-str', 'rot'])
    async def rotate(self, ctx: Context, n: Optional[int] = 1, *, text: str):
        """Obraca bity w podanym tekście"""
        bytes_ = ''.join(format(char, '0>8b') for char in bytearray(text, 'utf-8'))
        # n %= int(math.copysign(len(bytes_), n))
        bytes_ = bytes_[n:] + bytes_[:n]
        text = ''.join(chr(int(c, 2)) for c in chunk(bytes_, 8))

        if len(text) < 1024:
            await ctx.send(escape(text))
        else:
            await ctx.send(file=discord.File(io.BytesIO(text.encode()), 'text.json'))

    @commands.command(aliases=['leave'])
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    async def selfkick(self, ctx: Context):
        """Pomaga wyjść z serwera"""
        if ctx.author.top_role >= ctx.me.top_role or ctx.guild.owner_id == ctx.author.id:
            await ctx.error('Nie mogę')
            return

        await ctx.author.kick(reason='Użycie komendy selfkick')
        await ctx.ok_hand()


def setup(bot: Menel):
    bot.add_cog(Other())