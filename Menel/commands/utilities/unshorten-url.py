import aiohttp

from ...functions import bold, clean_content, code
from ...objects import Category, Command, Message


COMMAND = Command(
    'unshorten',
    syntax=None,
    description='Pokazuje dokąd porwadzi skrócony link.',
    category=Category.UTILS,
    cooldown=5
)


def setup(cliffs):
    @cliffs.command('(unshorten-url|unshorten|unshort) <url: url>', command=COMMAND)
    async def command(m: Message, url):
        urls = []
        shortened = False
        async with m.channel.typing():
            while True:
                async with aiohttp.request(
                        'HEAD',
                        url,
                        timeout=aiohttp.ClientTimeout(total=30),
                        allow_redirects=False
                ) as r:
                    urls.append(str(r.real_url))

                    if 'Location' in r.headers:
                        url = r.headers['Location']
                        if len(urls) >= 16 or url in urls:
                            shortened = True
                            break

                    else:
                        break

        if len(urls) <= 1:
            await m.error('Ten link nie jest skrócony')
            return

        if not shortened:
            *urls, last = urls
        else:
            last = None

        text = '\n'.join(code(clean_content(url, False, False, max_length=64)) for url in urls)
        text += '\n' * 2
        text += bold(code(clean_content(last, False, False, max_length=512))) if not shortened else '…'

        await m.info(text)