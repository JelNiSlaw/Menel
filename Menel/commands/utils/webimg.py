from asyncio import sleep
from io import BytesIO

from discord import File
from pyppeteer import launch
from pyppeteer.errors import NetworkError, PageError, TimeoutError

from ...objects.bot import bot
from ...objects.message import Message


def setup(cliffs):
    @cliffs.command('webimg [scrolling|fullpage]:fullpage <url...>', name='webimg', cooldown=10)
    async def command(m: Message, url, fullpage=None):
        async with m.channel.typing():
            browser = await launch(ignoreHTTPSErrors=True, headless=True, loop=bot.loop, args=['--no-sandbox'])
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