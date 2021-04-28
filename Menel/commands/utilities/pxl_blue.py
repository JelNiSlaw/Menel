import aiohttp

from ...functions import code
from ...helpers import pxl_blue
from ...objects import Category, Command, Message


COMMAND = Command(
    'pxl',
    syntax=None,
    description='Przesyła plik na pxl.blue.',
    aliases=('pxl.blue',),
    category=Category.UTILS,
    cooldown=10,
)

domains = []


def setup(cliffs):
    @cliffs.command('(pxl.blue|pxl) (list|[<domain...>]):sel', command=COMMAND)
    async def command(m: Message, sel, domain=None):
        if sel == 0:
            await m.info('Lista dostępnych domen:\n' + ' '.join(map(code, await get_domains())))
        else:
            if domain:
                domain = domain.casefold()
                if not any(map(lambda d: domain == d or domain.endswith('.' + d), await get_domains())):
                    await m.error('Podano nieprawidłową domenę')
                    return

            if not m.attachments:
                await m.error('Załącz plik do przesłania')
                return

            async with m.channel.typing():
                a = m.attachments[0]
                image = await pxl_blue.upload(await a.read(), a.filename, content_type=a.content_type, domain=domain)

            await m.success(f'Plik przesłano na {image.raw_url}')


async def get_domains():
    global domains

    if domains:
        return domains
    else:
        print('a')
        async with aiohttp.request(
                'GET', 'https://api.pxl.blue/domains',
                timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            json = await r.json()

        domains = [d['domain'] for d in json['domains']]
        return domains