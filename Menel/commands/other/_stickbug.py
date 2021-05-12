import asyncio
from io import BytesIO
from pathlib import Path
from time import perf_counter

import discord
from PIL import Image
from gsbl.stick_bug import StickBug

from ... import PATH
from ...functions import get_user
from ...functions.math import random_string
from ...objects import Category, Command, Message
from ...strings import USER_NOT_FOUND


COMMAND = Command(
    'stickbug',
    syntax=None,
    description='Wysyła darmowy dywan.',
    category=Category.OTHER,
    cooldown=3
)

TEMP_PATH = Path(PATH.parent / 'temp')
TEMP_PATH.mkdir(exist_ok=True)


def setup(cliffs):
    @cliffs.command('stickbug [<user...>]', command=COMMAND)
    async def command(m: Message, user=None):
        if user:
            if not (user := await get_user(user, m.guild)):
                await m.error(USER_NOT_FOUND)
                return
            image = user.avatar.replace(4096)
        elif m.attachments:
            if not (m.attachments[0]).content_type or \
                    not (m.attachments[0]).content_type.startswith('image/'):
                await m.error('Załącz jakiś obraz')
                return
            image = m.attachments[0]
        else:
            image = m.author.avatar.replace(4096)

        async with m.channel.typing():
            start = perf_counter()
            path = await asyncio.to_thread(generate_video, BytesIO(await image.read()))
            end = perf_counter()

        await m.send(
            f'Wyrenderowano w czasie {round(end - start, 1)}s',
            file=discord.File(path, 'video.mp4')
        )

        path.unlink(missing_ok=True)


def generate_video(image: BytesIO) -> Path:
    sb = StickBug(Image.open(image), video_resolution=(1024, 1024), lsd_scale=0.5)

    videopath = TEMP_PATH / (random_string(16) + '.mp4')
    audiopath = TEMP_PATH / (random_string(16) + '.wav')

    sb.process_video()

    sb.video.write_videofile(
        filename=str(videopath),
        codec='libx264',
        temp_audiofile=str(audiopath),
        preset='fast',
        logger=None
    )

    return videopath