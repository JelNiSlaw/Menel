from asyncio import sleep
from concurrent import futures
from io import BytesIO
from textwrap import dedent

import discord
from PIL import Image

from ...functions.imperialbin_upload import imperialbin_upload
from ...objects.message import Message


CHARSETS = (
    '█▓▒░ ',
    '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ',
    '@%+*:=-. '
)


def setup(cliffs):
    @cliffs.command('(ascii|asciiart|ascii-art) {[(blocks|standard|minimal):charset] [invert|inv|inverted]:invert}',
        name='asciiart', cooldown=5)
    async def command(m: Message, charset=0, invert=None):
        if not m.attachments:
            await m.error('Załącz najpierw jakiś plik.')
            return

        try:
            image = Image.open(BytesIO(await m.attachments[0].read()))  # download and open the file
        except discord.HTTPException:
            await m.error('Nie udało się pobrać załączonego pliku')
            return

        if image.width < 64 or image.height < 64:
            await m.error('To zdjęcie jest za małe.')
            return

        # generate ASCII art in a new thread
        ascii_img = await m.bot.loop.run_in_executor(
            futures.ThreadPoolExecutor(),
            lambda: image_to_ascii(
                image, CHARSETS[charset], invert is not None)
        )

        r = await imperialbin_upload(ascii_img, longer_urls=True, instant_delete=False, image_embed=True, expiration=1)

        if not r['success']:
            await m.error('Coś poszło nie tak podczas przesyłania obrazka.')
            return

        await sleep(2.5)

        await m.send(r['formattedLink'])


    def image_to_ascii(image, charset: list, invert: bool) -> str:
        if image.width >= image.height:
            image = image.resize((150, round(image.height / image.width * 75)), Image.LANCZOS)
        else:
            image = image.resize((round(image.width / image.height * 300), 150), Image.LANCZOS)

        if invert:
            charset = reversed(charset)

        image = image.convert('L')

        ascii_str = ''
        for pixel in image.getdata():
            ascii_str += charset[round(pixel / 255 * (len(charset) - 1))]

        ascii_img = ''

        for i in range(0, len(ascii_str), image.width):
            if not ascii_str[i:i + image.width].strip():
                continue
            ascii_img += ascii_str[i:i + image.width].rstrip() + '\n'

        return dedent(ascii_img)