from os import getenv

import aiohttp

from ...functions import clean_content
from ...objects import Category, Command, Message


COMMAND = Command(
    'pxseu',
    syntax=None,
    description='Wysyła wiadomość przez API pxseu.',
    category=Category.OTHER,
    cooldown=5
)


def setup(cliffs):
    @cliffs.command('pxseu {[(name|nick) <name>][(attachment|att|image|img) <url>]} [<message...>]', command=COMMAND)
    async def command(m: Message, message=None, name=None, url=None):
        if url:
            attachment = url
        elif m.attachments:
            attachment = m.attachments[0].url
        else:
            attachment = None

        async with aiohttp.request(
                'POST', 'https://www.pxseu.com/api/v2/sendMessage',
                json={
                    'message': message,
                    'name': name,
                    'attachment': attachment,
                    'user': m.author.id
                },
                headers={'Authorization': 'Bearer ' + getenv('PXSEU_MESSAGE_TOKEN')},
                timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            json = await r.json()

        if json['status'] == 200:
            await m.success('good')
        else:
            await m.error(f'{json["status"]}: {clean_content(json["message"])}')