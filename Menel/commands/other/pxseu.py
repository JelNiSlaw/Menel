from os import getenv

import aiohttp

from ...functions import clean_content
from ...objects import Category, Command, Message


COMMAND = Command(
    'pxseu',
    syntax=None,
    description='Wysyła wiadomość przez API pxseu.',
    category=Category.OTHER,
    cooldown=10
)


def setup(cliffs):
    @cliffs.command('pxseu {[(name|nick) <name>][(attachment|att|image|img) <url>]} [<message...>]', command=COMMAND)
    async def command(m: Message, message=None, name=None, url=None):
        if not url and m.attachments:
            url = m.attachments[0].url

        async with aiohttp.request(
                'POST', 'https://www.pxseu.com/api/v2/sendMessage',
                json={
                    'message': message,
                    'name': name,
                    'attachment': url,
                    'user': m.author.id
                },
                headers={'Authorization': 'Bearer ' + getenv('PXSEU_MESSAGE_TOKEN')},
                timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            json = await r.json()

        message = clean_content(json['message'])

        if r.status == 200:
            await m.success(message)
        else:
            if 'retry_after' in json:
                message += f'\nTry again in {json["retry_after"]}s'

            await m.error(f'{r.status}: {message}')