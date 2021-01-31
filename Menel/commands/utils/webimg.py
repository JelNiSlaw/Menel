import http.client
from asyncio import sleep
from io import BytesIO

from discord import File
from pyppeteer import launch
from pyppeteer.errors import NetworkError, PageError, TimeoutError

from ...objects.bot import bot
from ...objects.commands import Command
from ...objects.message import Message


COMMAND = Command(
    'webimg',
    syntax=None,
    description='Wykonuje zdjęcie wybranej strony.',
    cooldown=5
)


def setup(cliffs):
    @cliffs.command('webimg [scrolling|fullpage]:fullpage <url...>', command=COMMAND)
    async def command(m: Message, url, fullpage=None):
        if not m.channel.nsfw:
            await m.error('Websites can contain NSFW content.\nThis command only works on channels marked as NSFW.')
            return

        async with m.channel.typing():
            try:
                browser = await launch(ignoreHTTPSErrors=True, headless=True, loop=bot.loop, args=['--no-sandbox'])
            except http.client.BadStatusLine:
                await m.error('Nie udało się otworzyć przeglądarki. Spróbuj ponownie.')
                return

            page = await browser.newPage()
            await page.setViewport({'width': 2048, 'height': 1024, 'deviceScaleFactor': 2})

            try:
                await page.goto(url, timeout=60000)
            except TimeoutError:
                await m.error('Minął czas na wczytanie strony.')
            except (PageError, NetworkError):
                await m.error('Nie udało się wczytać strony. Sprawdź czy podany adres jest poprawny.')
            else:
                await sleep(2)

                try:
                    screenshot = await page.screenshot(
                        type='png',
                        fullPage=fullpage is not None,
                        encoding='binary'
                    )
                except NetworkError as e:
                    await m.error(str(e))
                else:
                    await m.send(file=File(BytesIO(screenshot), 'screenshot.png'))

            finally:
                await browser.close()