import asyncio
import mimetypes
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
    def __init__(self, *, only_audio: bool = False):
        self.status = {}

        self.OPTIONS = {
            'format': 'best',
            'outtmpl': str(PATH / 'temp' / (unique_id() + '.%(ext)s')),
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
        return await asyncio.to_thread(self.ydl.extract_info, video, False)


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
    @cliffs.command('(youtube-dl|youtubedl|yt-dl|ytdl|download|dl) [audio]:audio <video...>', command=COMMAND)
    async def command(m: Message, audio, video):
        await m.channel.trigger_typing()
        downloader = Downloader(only_audio=audio)

        progress_message = None
        try:
            info = await downloader.extract_info(video)

            if '_type' in info and info['_type'] == 'playlist':
                info = info['entries'][0]

            duration = info.get('duration')
            filesize = info.get('filesize')

            if not duration and not filesize:
                await m.error('Nieznana długość i rozmiar filmu')
                return

            if duration and duration > 60 * 30:
                await m.error('Maksymalna długość filmu to 30 minut')
                return

            if filesize and filesize > 100 * filesizes.MiB:
                await m.error('Maksymalny rozmiar filmu to 100 MiB')
                return

            progress_message = asyncio.create_task(downloader.progress_message(m))
            await downloader.download(info['webpage_url'])
        except youtube_dl.utils.YoutubeDLError as e:
            if progress_message:
                progress_message.cancel()

            await m.error(clean_content('\n'.join(e.args), max_length=1024, max_lines=16))
            return

        path = Path(downloader.status['filename'])

        try:
            async with m.channel.typing():
                with open(path, 'rb') as f:
                    file = await pxl_blue.upload(
                        f.read(),
                        '.'.join((info['title'], path.suffix)),
                        content_type=mimetypes.types_map.get('.' + path.suffix)
                    )
        finally:
            path.unlink(missing_ok=True)

        await m.send(file.raw_url)