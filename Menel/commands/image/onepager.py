import asyncio
import re
import textwrap
from io import BytesIO
from math import sqrt
from time import perf_counter

import discord
from PIL import Image, ImageDraw, ImageFont

from ... import PATH
from ...objects import Category, Command, Message


MAX_TEXT_LENGTH = 1024 * 512
MARGIN = 64
FONT = ImageFont.truetype(str(PATH / 'resources' / 'Roboto-Light.ttf'), size=20)

COMMAND = Command(
    'onepager',
    syntax=None,
    description='',
    category=Category.IMAGE,
    cooldown=20
)


def setup(cliffs):
    @cliffs.command('onepager', command=COMMAND)
    async def command(m: Message):
        if not m.attachments or \
                not (m.attachments[0]).content_type or \
                not (m.attachments[0]).content_type.startswith('text/'):
            await m.error('Załącz plik tekstowy')
            return

        attachment = m.attachments[0]

        text = prepare_text((await attachment.read()).decode('utf8'))

        if len(text) > MAX_TEXT_LENGTH:
            await m.error(f'Maksymalna długość tekstu to {MAX_TEXT_LENGTH} znaków')
            return

        async with m.channel.typing():
            start = perf_counter()
            image = await asyncio.to_thread(render_page, text)
            end = perf_counter()
            await m.send(
                f'Wyrenderowano w czasie {round(end - start, 1)}s',
                file=discord.File(image, attachment.filename.rsplit('.', 1)[0] + '.png')
            )


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
    size = FONT.getsize_multiline(text)
    image = Image.new('L', (size[0] + 2 * MARGIN, size[1] + 2 * MARGIN), 0xffffff)

    draw = ImageDraw.Draw(image)
    draw.multiline_text((MARGIN, MARGIN), text, fill=0, font=FONT, align='center')

    file = BytesIO()
    image.save(file, format='png', optimize=True, dpi=(96, 96))
    file.seek(0)

    return file