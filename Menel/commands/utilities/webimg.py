import http.client
from asyncio import sleep

import discord
from pyppeteer import launch
from pyppeteer.errors import NetworkError, PageError, TimeoutError

from ...functions import embed_with_author
from ...helpers import pxl_blue
from ...objects import Category, Command, Message


COMMAND = Command(
    'webimg',
    syntax=None,
    description='Wykonuje zdjęcie wybranej strony.',
    category=Category.UTILS,
    cooldown=5
)


def setup(cliffs):
    @cliffs.command('(webimg|webshot) [scrolling|fullpage]:fullpage <url: url>', command=COMMAND)
    async def command(m: Message, url, fullpage=None):
        async with m.channel.typing():
            try:
                browser = await launch(
                    ignoreHTTPSErrors=True, headless=True, args=['--no-sandbox', '--disable-dev-shm-usage']
                )
            except http.client.BadStatusLine:
                await m.error('Nie udało się otworzyć przeglądarki. Spróbuj ponownie.')
                return

            page = await browser.newPage()
            await page.setViewport({'width': 2048, 'height': 1024, 'deviceScaleFactor': 1 if fullpage else 2})

            try:
                await page.goto(url, timeout=30000)
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
                    embed = discord.Embed(colour=discord.Colour.green())
                    embed = embed_with_author(m.author, embed)

                    upload = await pxl_blue.upload(screenshot, 'screenshot.png', content_type='image/png')

                    if m.channel.nsfw:
                        embed.set_image(url=upload.raw_url)
                        await m.send(embed=embed)
                    else:
                        embed.description = f'Zdjęcie strony: {upload.raw_url}'
                        embed.set_footer(text='Podgląd dostępny jest jedynie na kanałach NSFW')

                        await m.send(embed=embed)

            finally:
                await browser.close()