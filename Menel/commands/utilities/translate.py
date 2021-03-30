import aiohttp
import discord
from googletrans.constants import LANGCODES, LANGUAGES

from ...functions import clean_content, embed_with_author
from ...objects import Category, Command, Message


COMMAND = Command(
    'translate',
    syntax=None,
    description='Tłumaczy tekst na inny język.',
    aliases=('trans', 'tr'),
    category=Category.UTILS,
    cooldown=2
)

AUTO = 'auto'


def setup(cliffs):
    @cliffs.command('(translate|trans|tr) {[from <src>] ([to] <dest>)} <text...>', command=COMMAND)
    async def command(m: Message, text, src=AUTO, dest='pl'):
        src = src.lower()
        dest = dest.lower()

        if src != AUTO and src not in LANGUAGES:
            if src in LANGCODES:
                src = LANGCODES[src]
            else:
                await m.error('Podano nieprawiłowy język źródłowy')
                return

        if dest != AUTO and dest not in LANGUAGES:
            if dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                await m.error('Podano nieprawiłowy język docelowy')
                return

        async with m.channel.typing():
            async with aiohttp.request(
                    'GET', 'https://translate.googleapis.com/translate_a/single',
                    params={
                        'sl': src,  # source language
                        'tl': dest,  # translation language
                        'q': text,  # query string
                        'client': 'gtx',  # probably Google Translate Extension
                        'dj': 1,  # what
                        'dt': 't'  # what even is this
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                json = await r.json()

            if 'sentences' not in json:
                await m.error('Tłumacz Google nie zwrócił tłumaczenia')
                return

            if src == AUTO:
                src = json.get('src', AUTO)

            embed = embed_with_author(m.author, discord.Embed(colour=discord.Colour.green()))
            embed.title = LANGUAGES.get(src, src).capitalize() + ' → ' + LANGUAGES.get(dest, dest).capitalize()
            embed.description = clean_content(
                ' '.join(s['trans'] for s in json['sentences']),
                max_length=2048,
                max_lines=32
            )

            await m.send(embed=embed)