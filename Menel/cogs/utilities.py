import asyncio
import http.client
import os
import re
import unicodedata
from io import BytesIO
from math import floor
from pathlib import Path
from typing import Literal, Optional
from urllib import parse

import aiohttp
import dateutil.parser
import discord
import pyppeteer
import pyppeteer.errors
import unidecode
import youtube_dl
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter

from .. import PATH
from ..bot import Menel
from ..resources import filesizes
from ..resources.languages import LANGUAGES
from ..utils import embeds, imgur, markdown
from ..utils.checks import has_attachments
from ..utils.context import Context
from ..utils.converters import LanguageConverter, URL
from ..utils.text_tools import escape, escape_str, limit_length, plural


AUTO = 'auto'


class YouTubeDownloader:
    def __init__(self, *, only_audio: bool = False):
        self.status = {}

        self.OPTIONS = {
            'format': 'best',
            'outtmpl': str(PATH / 'temp' / (os.urandom(16).hex() + '.%(ext)s')),
            'merge_output_format': 'mp4',
            'default_search': 'auto',
            'progress_hooks': [self._hook],
            'max_downloads': 1,
            'ignore_config': True,
            'no_playlist': True,
            'no_mark_watched': True,
            'geo_bypass': True,
            'no_color': True,
            'abort_on_error': True,
            'abort_on_unavailable_fragment': True,
            'no_overwrites': True,
            'no_continue': True,
            'quiet': True,
        }

        if only_audio:
            self.OPTIONS.update(format='bestaudio/best', extract_audio=True)

        self.ydl = youtube_dl.YoutubeDL(self.OPTIONS)

    async def download(self, video: str) -> None:
        self.status.clear()
        await asyncio.to_thread(self.ydl.extract_info, video)

    async def extract_info(self, video: str) -> dict:
        return await asyncio.to_thread(self.ydl.extract_info, video, download=False)

    def _hook(self, info: dict) -> None:
        self.status = info

    async def progress_message(self, m: Context):
        msg = await m.send('Downloading…')

        for _ in range(20):
            if self.status:
                break

            await asyncio.sleep(0.5)

        while self.status and self.status['status'] == 'downloading':
            ratio = self.status['downloaded_bytes'] / self.status['total_bytes']
            progress = ('\N{FULL BLOCK}' * floor(ratio * 20)).ljust(20, '\N{LIGHT SHADE}')
            await msg.edit(
                content=f"{progress} {ratio:.1%} "
                        f"{self.status['_speed_str'].strip()} Pozostało {self.status['_eta_str'].strip()}"
            )
            await asyncio.sleep(1.5)

        await msg.delete()


class Utilities(commands.Cog):
    @commands.command(aliases=['trans', 'tr'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def translate(self, ctx: Context, lang1: LanguageConverter, lang2: Optional[LanguageConverter], *, text: str):
        """
        Tłumaczy teskt Tłumaczem Google
        `lang1`: język docelowy, lub źródłowy jeśli podany jest argument `lang2`
        `lang2`: język docelowy jeśli podany jest argument `lang1`
        `text`: tekst do przetłumaczenia
        """
        if lang2 is not None:
            src = lang1
            dest = lang2
        else:
            src = AUTO
            dest = lang1

        async with ctx.typing():
            r = await ctx.bot.client.get(
                'https://translate.googleapis.com/translate_a/single',
                params={
                    'sl': src,  # source language
                    'tl': dest,  # translation language
                    'q': text,  # query
                    'client': 'gtx',  # Google Translate Extension
                    'dj': 1,  # what?
                    'dt': 't'  # what is this?
                }
            )
            json = await r.json()

            if 'sentences' not in json:
                await ctx.error('Tłumacz Google nie zwrócił tłumaczenia')
                return

            if src == AUTO:
                src = json.get('src', AUTO)

            embed = embeds.with_author(ctx.author)
            embed.title = LANGUAGES.get(src, src).title() + ' ➜ ' + LANGUAGES.get(dest, dest).title()
            embed.description = limit_length(
                escape(' '.join(s['trans'] for s in json['sentences'])),
                max_length=4096,
                max_lines=32
            )

        await ctx.send(embed=embed)

    @commands.command(aliases=['urban-dictionary', 'urban', 'ud'])
    async def urbandictionary(self, ctx: Context, *, query: str):
        """Wyszukuje podaną frazę w słowniku Urban Dictionary"""
        async with ctx.typing():
            r = await ctx.client.head(
                'https://www.urbandictionary.com/define.php',
                params={'term': query},
                allow_redirects=False
            )
            if r.status_code == 200:
                query = parse.quote(query)
            elif r.status_code == 302:
                query = r.headers['Location'].split('term=', 1)[1]
            else:
                await ctx.error('Nie znalazłem tej frazy w Urban Dictionary.')
                return

            r = await ctx.client.get('https://api.urbandictionary.com/v0/define', params={'term': query})
            json = r.json()

        if 'error' in json:
            await ctx.error(f'Urban Dictionary zwróciło błąd:\n{json["error"]}')
            return

        data = json['list'][0]

        def remove_brackets(text: str) -> str:
            return re.sub(r'\[(?P<word>.*?)]', r'\g<word>', text, re.DOTALL)

        embed = discord.Embed(
            title=limit_length(data['word'], max_length=256),
            url=data['permalink'],
            description=escape(limit_length(remove_brackets(data['definition']), max_length=2048, max_lines=16)),
            color=discord.Color.green()
        )

        if data['example']:
            embed.add_field(
                name='Example',
                value=limit_length(escape(remove_brackets(data['example'])), max_length=1024, max_lines=16),
                inline=False
            )

        embed.set_footer(text=f"Author: {data['author']}\n👍 {data['thumbs_up']} 👎 {data['thumbs_down']}")
        embed.timestamp = dateutil.parser.parse(data['written_on'])
        await ctx.send(embed=embed)

    @commands.command(aliases=['m', 'calculate', 'calculator', 'calc', 'kalkulator'])
    async def math(self, ctx: Context, *, expression: str):
        """Kalkulator Stanisław Jelnicki"""
        async with ctx.channel.typing():
            if re.sub(r'\s+', '', expression) == '2+2':
                await asyncio.sleep(0.5)
                await ctx.send('5')
                return

            r = await ctx.client.post('https://api.mathjs.org/v4/', json={'expr': expression})
            json = r.json()

        if json['error']:
            await ctx.error(escape(limit_length(json['error'], max_length=1024, max_lines=4)))
            return

        await ctx.send(escape(limit_length(json['result'], max_length=2048, max_lines=16)))

    @commands.command()
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def eval(self, ctx: Context, *, code: codeblock_converter):
        """Bezpiecznie wykonuje podany kod w wybranym języku"""
        language, code = code

        if not language:
            await ctx.error('Umieść kod w bloku:\n\\`\\`\\`język\nkod\n\\`\\`\\`')
            return

        if not code.strip():
            await ctx.error('Podaj kod do wykonania.')
            return

        async with ctx.channel.typing():
            async with aiohttp.request(
                    'POST',
                    'https://emkc.org/api/v1/piston/execute',
                    json={'language': language, 'source': code}
            ) as r:
                json = await r.json()
            if r.status != 200:
                await ctx.error(json.get('message', 'Nieznany błąd.'))
                return

            output = [markdown.codeblock(limit_length(json[out], max_length=512, max_lines=16))
                for out in ('stdout', 'stderr') if json[out].strip()]

            embed = discord.Embed(
                description=('\n'.join(output) if output else
                             'Twój kod nic nie wypisał.') +
                            f'\n{json["language"]} {json["version"]}\n'
                            f'Powered by [Piston](https://github.com/engineer-man/piston).',
                color=discord.Color.green() if not json['stderr'].strip() else discord.Color.red()
            )

        await ctx.send(embed=embed)

    @commands.command(aliases=['charinfo', 'utf', 'utf8', 'utf-8', 'u'])
    async def unicode(self, ctx: Context, *, chars: str):
        """Pokazuje nazwy znaków standardu Unicode"""
        output = []
        for c in chars[:16]:
            if c == '\u0020':  # space
                output.append('')
                continue

            info = f"{escape_str(c)} \N{EM DASH} U+{ord(c):0>4X}"
            try:
                info += f' \N{EM DASH} {unicodedata.name(c)}'
            except ValueError:
                pass

            output.append(info)

        if len(chars) > 16:
            output.append('...')

        await ctx.send(markdown.codeblock('\n'.join(output)))

    @commands.command()
    async def unidecode(self, ctx: Context, *, text: str):
        """Zamienia znaki Unicode na ASCII używając [unidecode](https://github.com/avian2/unidecode)"""
        await ctx.send(escape(limit_length(unidecode.unidecode(text), max_length=1024, max_lines=16), markdown=False))

    @commands.command(aliases=['mc', 'skin'])
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def minecraft(self, ctx: Context, *, player: str):
        """Wysyła skin konta Minecraft Java Edition"""
        async with ctx.channel.typing():
            r = await ctx.client.get(f'https://api.mojang.com/users/profiles/minecraft/{parse.quote(player)}')
            if r.status_code == 204:
                await ctx.error('Nie znalazłem gracza o tym nicku.')
                return

            json = r.json()
            uuid = json['id']

            requests = [(f'https://api.mojang.com/user/profiles/{uuid}/names', None),
                (f'https://crafatar.com/avatars/{uuid}', {'size': '256', 'overlay': None}),
                (f'https://crafatar.com/renders/head/{uuid}', {'scale': '6', 'overlay': None}),
                (f'https://crafatar.com/renders/body/{uuid}', {'scale': '10', 'overlay': None})]

            responses = await asyncio.gather(*(ctx.client.get(url, params=params) for (url, params) in requests))
            name_history = responses[0].json()
            avatar, head, body = (r.read() for r in responses[1:])

            name_history = ', '.join(escape(name['name']) for name in name_history)
            avatar = discord.File(BytesIO(avatar), 'avatar.png')
            head = discord.File(BytesIO(head), 'head.png')
            body = discord.File(BytesIO(body), 'body.png')

            embed = discord.Embed(
                description=f'Historia nazw: {name_history}\nUUID: `{uuid}`',
                color=discord.Color.green()
            )
            embed.set_author(name=json['name'], icon_url='attachment://head.png')
            embed.set_thumbnail(url='attachment://avatar.png')
            embed.set_image(url='attachment://body.png')

        await ctx.send(embed=embed, files=[avatar, head, body])

    @commands.command(aliases=['webshot'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.max_concurrency(3, wait=True)
    async def webimg(self, ctx: Context, fullpage: Optional[Literal['fullpage', 'full']], *, url: URL):
        """Robi i wysyła zrzut ekranu strony internetowej"""
        async with ctx.typing():
            try:
                browser = await pyppeteer.launch(
                    ignoreHTTPSErrors=True, headless=True, args=['--no-sandbox', '--disable-dev-shm-usage']
                )
            except http.client.BadStatusLine:
                await ctx.error('Nie udało się otworzyć przeglądarki. Spróbuj ponownie.')
                return

            page = await browser.newPage()
            await page.setViewport(
                {'width': 2048, 'height': 1024, 'deviceScaleFactor': 1 if fullpage is not None else 2}
            )

            try:
                await page.goto(url, timeout=30000)
            except TimeoutError:
                await ctx.error('Minął czas na wczytanie strony.')
            except (pyppeteer.errors.PageError, pyppeteer.errors.NetworkError):
                await ctx.error('Nie udało się wczytać strony. Sprawdź czy podany adres jest poprawny.')
            else:
                await asyncio.sleep(2)

                try:
                    screenshot = await page.screenshot(
                        type='png', fullPage=fullpage is not None, encoding='binary'
                    )
                except pyppeteer.errors.NetworkError as e:
                    await ctx.error(str(e))
                else:
                    embed = embeds.with_author(ctx.author)
                    image = await imgur.upload_image(screenshot)

                    embed.description = f'Zdjęcie strony: {image}'
                    if ctx.channel.nsfw:
                        embed.set_image(url=image)
                    else:
                        embed.set_footer(text='Podgląd dostępny jest wyłącznie na kanałach NSFW')

                    await ctx.send(embed=embed)
            finally:
                await browser.close()

    @commands.command('unshorten-url', aliases=['unshorten', 'unshort'])
    async def unshorten_url(self, ctx: Context, *, url: URL):
        """Pokazuje przekierowania skróconego linku"""
        urls = []
        shortened = False
        async with ctx.typing():
            while True:
                async with aiohttp.request(
                        'HEAD', url, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    urls.append(str(r.real_url))

                    if 'Location' not in r.headers:
                        break

                    url = r.headers['Location']
                    if len(urls) >= 16 or url in urls:
                        shortened = True
                        break

        if len(urls) <= 1:
            await ctx.error('Ten link nie jest skrócony')
            return

        if not shortened:
            *urls, last = urls
        else:
            last = None

        text = [markdown.code(limit_length(url, max_length=64)) for url in urls]
        text.append(limit_length(last, max_length=512) if not shortened else '…')
        await ctx.embed('\n'.join(text))

    @commands.command(aliases=['rtfm'])
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.cooldown(3, 5)  # API rate limit
    async def docs(self, ctx: Context, *, query: str):
        """Przeszukuje dokumentację biblioteki discord.py (gałęzi master)"""
        r = await ctx.client.get(
            'https://idevision.net/api/public/rtfm', params={
                'show-labels': True,
                'label-labels': False,
                'location': 'https://discordpy.readthedocs.io/en/master/',
                'query': query
            }
        )

        json = r.json()
        nodes = json['nodes']

        if not nodes:
            await ctx.error('Nie znaleziono żadnych pasujących wyników')
            return

        text = [f'[{markdown.code(name)}]({url})' for name, url in nodes.items()]

        embed = embeds.with_author(
            ctx.author,
            title=plural(len(nodes), 'wynik', 'wyniki', 'wyników'),
            description='\n'.join(text),
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Czas wyszukiwania: {float(json['query_time']) * 1000:.0f} ms")
        await ctx.send(embed=embed)

    @commands.command('youtube-dl', aliases=['youtubedl', 'yt-dl', 'ytdl', 'download', 'dl'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.max_concurrency(2)
    async def youtube_dl(self, ctx: Context, audio: Optional[Literal['audio']], *, video: str):
        """
        Pobiera film ze strony
        `audio`: pobiera jedynie dźwięk filmu
        `video`: link do strony z filmem
        """
        await ctx.channel.trigger_typing()
        downloader = YouTubeDownloader(only_audio=audio is not None)

        progress_message = None
        try:
            info = await downloader.extract_info(video)

            if '_type' in info and info['_type'] == 'playlist':
                info = info['entries'][0]

            duration = info.get('duration')
            filesize = info.get('filesize')

            if not duration and not filesize:
                await ctx.error('Nieznana długość i rozmiar filmu')
                return

            if duration and duration > 60 * 30:
                await ctx.error('Maksymalna długość filmu to 30 minut')
                return

            if filesize and filesize > 200 * filesizes.MiB:
                await ctx.error('Maksymalny rozmiar filmu to 100 MiB')
                return

            progress_message = asyncio.create_task(downloader.progress_message(ctx))
            await downloader.download(info['webpage_url'])
        except youtube_dl.utils.YoutubeDLError as e:
            if progress_message:
                progress_message.cancel()

            await ctx.error(escape(limit_length('\n'.join(e.args), max_length=1024, max_lines=16)))
            return

        path = Path(downloader.status['filename'])

        try:
            async with ctx.channel.typing():
                with open(path, 'rb') as f:
                    video = await imgur.upload_video(f.read())
        finally:
            path.unlink(missing_ok=True)

        await ctx.send(video)

    @commands.command('imgur')
    @has_attachments(allowed_types=('image/',))
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _imgur(self, ctx: Context):
        """Przesyła załączone zdjęcia na Imgur"""
        async with ctx.typing():
            images = [await imgur.upload_image(await a.read()) for a in ctx.message.attachments]
            await ctx.send('\n'.join(f'<{image}>' for image in images))


def setup(bot: Menel):
    bot.add_cog(Utilities())