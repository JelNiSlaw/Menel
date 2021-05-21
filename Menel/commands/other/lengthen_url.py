import aiohttp

from ...objects import Category, Command, Message


COMMAND = Command(
    'lengthen-url',
    syntax=None,
    description='Wydłuża zbyt krótki link.',
    category=Category.OTHER,
    cooldown=3
)


def setup(cliffs):
    @cliffs.command('(lengthen-url|lengthen) <url: url>', command=COMMAND)
    async def command(m: Message, url):
        if len(url) > 512:
            await m.error('Przekroczono maksymalną długość linku')
            return

        with m.channel.typing():
            async with aiohttp.request(
                    'GET', 'https://api.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com/a',
                    params={'url': url},
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                content = await r.text()

            if content == 'INVALID_URL':
                await m.error('Podano nieprawidłowy adres URL')
                return

        await m.send(content)