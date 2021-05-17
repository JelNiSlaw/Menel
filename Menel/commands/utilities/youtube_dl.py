import asyncio
from math import floor
from pathlib import Path

import youtube_dl

from ... import PATH
from ...functions import clean_content
from ...functions.math import unique_id
from ...helpers import pxl_blue
from ...objects import Category, Command, Message
from ...resources import filesizes


COMMAND = Command(
    'youtube-dl',
    syntax=None,
    description='Pobiera film z internetu używając youtube-dl.',
    category=Category.UTILS,
    cooldown=2
)


class Downloader:
    def __init__(self, video: str):
        self.video = video
        self.status = {}

        self.OPTIONS = {
            'limit-rate': '0.1M',
            'format': 'best',
            'outtmpl': str(PATH / 'temp' / (unique_id() + '.%(ext)s')),
            'merge-output-format': 'mp4',
            'progress_hooks': [self._hook],
            'max-downloads': 1,
            'ignore-config': True,
            'no-playlist': True,
            'no-mark-watched': True,
            'geo-bypass': True,
            'no_color': True,
            'abort-on-error': True,
            'abort-on-unavailable-fragment': True,
            'no-overwrites': True,
            'no-continue': True,
            'quiet': True,
        }


    async def download(self) -> None:
        self.status.clear()

        with youtube_dl.YoutubeDL(self.OPTIONS) as ydl:
            await asyncio.to_thread(ydl.extract_info, self.video)


    async def extract_info(self) -> dict:
        with youtube_dl.YoutubeDL(self.OPTIONS) as ydl:
            return await asyncio.to_thread(ydl.extract_info, self.video, False)


    def _hook(self, info: dict) -> None:
        self.status = info


    async def progress_message(self, m: Message):
        msg = await m.send('Downloading…')

        for _ in range(20):
            if self.status:
                break

            await asyncio.sleep(0.5)

        while self.status and self.status['status'] == 'downloading':
            ratio = self.status['downloaded_bytes'] / self.status['total_bytes']
            progress = ('█' * floor(ratio * 10)).ljust(10, '░')
            await msg.edit(
                content=f"{progress} {ratio:.1%} "
                        f"{self.status['_speed_str'].strip()} Pozostało {self.status['_eta_str'].strip()}"
            )
            await asyncio.sleep(1.5)

        await msg.delete()


def setup(cliffs):
    @cliffs.command('(youtube-dl|youtubedl|yt-dl|ytdl|download|dl) <video...>', command=COMMAND)
    async def command(m: Message, video):
        await m.channel.trigger_typing()
        downloader = Downloader(video)

        progress_message = None
        try:
            info = await downloader.extract_info()

            if not info.get('duration'):
                await m.error('Nieznana długość filmu')
                return

            if info['duration'] > 600:
                await m.error('Maksymalna długość filmu to 10 minut')
                return

            if (info.get('filesize') or 0) > 100 * filesizes.MiB:
                await m.error('Maksymalny rozmiar filmu to 100 MiB')
                return

            progress_message = asyncio.create_task(downloader.progress_message(m))
            await downloader.download()
        except youtube_dl.utils.YoutubeDLError as e:
            if progress_message:
                progress_message.cancel()

            await m.error(clean_content('\n'.join(e.args), max_length=1024, max_lines=16))
            return

        async with m.channel.typing():
            path = Path(downloader.status['filename'])

            with open(path, 'rb') as f:
                file = await pxl_blue.upload(f.read(), f"{info['title']}.{info['ext']}", content_type='video/mp4')

        await m.send(file.raw_url)

        path.unlink(True)