import asyncio
import imghdr
import re
import textwrap
from io import BytesIO
from math import sqrt
from os import environ
from time import perf_counter
from typing import Literal, Optional

import discord
import httpx
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from .. import PATH
from ..bot import Menel
from ..utils import imperial
from ..utils.checks import has_attachments
from ..utils.context import Context


ASCII_IMG_SIZE = 128
ASCII_STYLES = {
    'blocks': '█▓▒░ ',
    'standard': '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ',
    'minimal': '@%+*:=-. '
}

ONEPAGER_MAX_TEXT_LENGTH = 512 * 1024
ONEPAGER_MARGIN = 64
ONEPAGER_FONT = ImageFont.truetype(str(PATH / 'resources' / 'Roboto-Light.ttf'), size=20)


def image_to_ascii(image: Image, charset: str, invert: bool) -> str:
    if image.width >= image.height:
        size = ASCII_IMG_SIZE, round((image.height / image.width) * (ASCII_IMG_SIZE // 2))
    else:
        size = round((image.width / image.height) * (ASCII_IMG_SIZE * 2)), ASCII_IMG_SIZE

    image = image.resize(size, Image.LANCZOS)

    if image.mode != 'L':
        if not invert:
            white = Image.new('RGB', image.size, color=0xFFFFFF)
            white.paste(image, mask=image)

        image = image.convert('L', dither=Image.NONE)

    if invert:
        charset = charset[::-1]

    ascii_image = ''
    imagedata = list(image.getdata())
    for i in range(0, image.width * image.height - 1, image.width):
        row = (charset[round(pixel / 255 * (len(charset) - 1))] for pixel in imagedata[i:i + image.width])
        ascii_image += ''.join(row).rstrip() + '\n'

    return ascii_image


def prepare_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.strip())
    return '\n'.join(
        textwrap.wrap(
            text,
            width=round(sqrt(len(text)) * 1.25),
            expand_tabs=False,
            replace_whitespace=True,
            drop_whitespace=True,
            break_on_hyphens=False
        )
    )


def render_page(text: str) -> BytesIO:
    size = ONEPAGER_FONT.getsize_multiline(text)
    image = Image.new('L', (size[0] + 2 * ONEPAGER_MARGIN, size[1] + 2 * ONEPAGER_MARGIN), 0xffffff)

    draw = ImageDraw.Draw(image)
    draw.multiline_text((ONEPAGER_MARGIN, ONEPAGER_MARGIN), text, fill=0, font=ONEPAGER_FONT, align='center')

    file = BytesIO()
    image.save(file, format='png', optimize=True)
    file.seek(0)

    return file


class Images(commands.Cog):
    @commands.command(aliases=['ascii-art', 'ascii'])
    @has_attachments(1, ('image/',))
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.max_concurrency(3)
    async def asciiart(
            self,
            ctx: Context,
            style: Optional[Literal['blocks', 'standard', 'minimal']] = 'blocks',
            invert: Literal['invert', 'inv', 'inverted'] = False
    ):
        """
        Generuje ASCII art z załączonego zdjęcia
        `style`: zestaw znaków
        `invert`: zamiana ciemnych znaków z jasnymi
        """
        try:
            image = Image.open(BytesIO(await ctx.message.attachments[0].read()))
        except discord.HTTPException:
            await ctx.error('Nie udało się pobrać załączonego pliku')
            return

        if image.width < 64 or image.height < 64:
            await ctx.error('Ten obraz jest za mały')
            return

        image = await asyncio.to_thread(image_to_ascii, image, ASCII_STYLES[style], invert is not None)
        document = await imperial.create_document(image, short_urls=True, expiration=14)
        await ctx.send(document.raw_link)

    @commands.command(aliases=['burning'])
    async def cooltext(self, ctx: Context, *, text: str):
        """Generuje palący się tekst na stronie cooltext.com"""
        async with ctx.channel.typing():
            r = await ctx.client.post(
                'https://cooltext.com/PostChange', data={
                    'LogoID': 4,
                    'Text': text,
                    'FontSize': 70,
                    'Color1_color': '#FF0000',
                    'Integer1': 15,
                    'Boolean1': 'on',
                    'Integer13': 'on',
                    'Integer12': 'on',
                    'BackgroundColor_color': '#000000'
                }
            )

            async with httpx.AsyncClient(verify=False) as client:
                r = await client.get(r.json()['renderLocation'])

        await ctx.send(file=discord.File(BytesIO(r.read()), 'burning.gif'))

    @commands.command(aliases=['jesus', 'jestsus'])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def jezus(self, ctx: Context):
        """Wysyła losowe zdjęcie Jezusa"""
        async with ctx.channel.typing():
            r = await ctx.client.get(
                'https://obrazium.com/v1/jesus', headers={'Authorization': environ['OBRAZIUM_TOKEN']}
            )
            if r.status_code == 200:
                file = BytesIO(r.read())
                ext = imghdr.what(file) or 'jpeg'
                await ctx.send(file=discord.File(file, filename='jezus.' + ext))
            else:
                await ctx.error('Nie działa')

    @commands.command()
    @has_attachments(1, ('text/',))
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.max_concurrency(2)
    async def onepager(self, ctx: Context):
        """Renderuje cały załączony plik tesktowy na jednej stronie"""
        attachment = ctx.message.attachments[0]

        if not attachment.content_type or not attachment.content_type.startswith('text/'):
            await ctx.error('Załącz plik tekstowy')
            return

        text = prepare_text((await attachment.read()).decode('utf8'))

        if len(text) > ONEPAGER_MAX_TEXT_LENGTH:
            await ctx.error(f'Maksymalna długość tekstu to {ONEPAGER_MAX_TEXT_LENGTH} znaków')
            return

        async with ctx.channel.typing():
            start = perf_counter()
            image = await asyncio.to_thread(render_page, text)
            end = perf_counter()
            await ctx.send(
                f'Wyrenderowano w czasie {round(end - start, 1)}s',
                file=discord.File(image, attachment.filename.rsplit('.', 1)[0] + '.png')
            )

    @commands.command(aliases=['this-person-does-not-exist', 'thispersondoesnotexist', 'person'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def tpdne(self, ctx: Context):
        """Pobiera wygenerowaną twarz z thispersondoesnotexist.com"""
        async with ctx.channel.typing():
            r = await ctx.client.get('https://thispersondoesnotexist.com/image')
        await ctx.send(file=discord.File(BytesIO(r.read()), filename='person.jpeg'))


def setup(bot: Menel):
    bot.add_cog(Images())