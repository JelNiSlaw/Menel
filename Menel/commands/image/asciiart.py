import asyncio
from io import BytesIO

import discord
from PIL import Image

from ...helpers import imperial
from ...objects import Category, Command, Message


COMMAND = Command(
    'asciiart',
    syntax=None,
    description='Tworzy ASCII art z załączonego obrazka',
    aliases=('ascii-art', 'ascii'),
    category=Category.IMAGE,
    cooldown=5
)

CHARSETS = (
    '█▓▒░ ',
    '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ',
    '@%+*:=-. '
)

IMG_SIZE = 128


def setup(cliffs):
    @cliffs.command(
        '(asciiart|ascii-art|ascii) {[(blocks|standard|minimal):charset] [invert|inv|inverted]:invert}',
        command=COMMAND
    )
    async def command(m: Message, charset=0, invert=None):
        if not m.attachments:
            await m.error('Załącz jakiś obraz')
            return

        try:
            image = Image.open(BytesIO(await m.attachments[0].read()))
        except discord.HTTPException:
            await m.error('Nie udało się pobrać załączonego pliku')
            return

        if image.width < 64 or image.height < 64:
            await m.error('To zdjęcie jest za małe')
            return

        image = await asyncio.to_thread(image_to_ascii, image, CHARSETS[charset], invert is not None)
        document = await imperial.create_document(image, expiration=14)
        await m.send(document.raw_link)


def image_to_ascii(image: Image, charset: str, invert: bool) -> str:
    if image.width >= image.height:
        size = IMG_SIZE, round((image.height / image.width) * (IMG_SIZE // 2))
    else:
        size = round((image.width / image.height) * (IMG_SIZE * 2)), IMG_SIZE

    image = image.resize(size, Image.LANCZOS)

    if image.mode != 'L':
        if not invert:
            white = Image.new('RGB', image.size, color=0xFFFFFF)
            white.paste(image, mask=image)
            image = white.convert('L', dither=Image.NONE)
        else:
            image = image.convert('L', dither=Image.NONE)

    if invert:
        charset = charset[::-1]

    ascii_image = ''
    imagedata = list(image.getdata())
    for i in range(0, image.width * image.height - 1, image.width):
        row = (charset[round(pixel / 255 * (len(charset) - 1))] for pixel in imagedata[i:i + image.width])
        ascii_image += ''.join(row).rstrip() + '\n'

    return ascii_image