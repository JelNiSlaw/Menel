import random
from os import getenv
from typing import Optional

import aiohttp
from discord.ext import commands

from ..objects.context import Context
from ..utils.converters import URL
from ..utils.formatting import codeblock
from ..utils.text_tools import clean_content


class PxseuFlags(commands.FlagConverter, case_insensitive=True):
    name: Optional[str]
    url: Optional[URL]
    message: Optional[str]


class Other(commands.Cog, name='Inne'):
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

        lines = []
        for _ in range(length):
            lines.append(f"┃{''.join(random.choice('╱╲') for _ in range(width))}┃")

        line = '━' * width
        lines.insert(0, f'┏{line}┓')
        lines.append(f'┗{line}┛')
        lines = codeblock('\n'.join(lines), escape=False)
        await ctx.info(f'Proszę, oto Twój darmowy dywan\n{lines}')

    @commands.command(aliases=['px'], ignore_extra=False, hidden=True)
    async def pxseu(self, ctx: Context, *, flags: PxseuFlags):
        """
        Wysyła anonimową wiadomość do pxseu
        `flags`: dane do wsyłania
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

        async with aiohttp.request(
                'POST', 'https://www.pxseu.com/api/v2/sendMessage',
                json={
                    'message': flags.message,
                    'name': flags.name,
                    'attachment': url,
                    'user': ctx.author.id
                },
                headers={'Authorization': 'Bearer ' + getenv('PXSEU_MESSAGE_TOKEN')},
                timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            json = await r.json()

        message = clean_content(json['message'])

        if r.status == 200:
            await ctx.info(message)
        else:
            if 'retry_after' in json:
                message += f'\nTry again in {json["retry_after"]}s'

            await ctx.error(f'{r.status}: {message}')

    @commands.command('lengthen-url', aliases=['lengthen'])
    async def lengthen_url(self, ctx: Context, *, url: URL):
        """Wydłuża zbyt krótki link"""
        if len(url) > 512:
            await ctx.error('Przekroczono maksymalną długość linku')
            return

        with ctx.channel.typing():
            async with aiohttp.request(
                    'GET', f"https://api.{'a' * 56}.com/a",
                    params={'url': url},
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                content = await r.text()

            if content == 'INVALID_URL':
                await ctx.error('Podano nieprawidłowy adres URL')
                return

        await ctx.send(content)

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


def setup(bot):
    bot.add_cog(Other())