from os import getenv

import aiohttp

from ...functions.clean_content import clean_content
from ...objects.commands import Command
from ...objects.message import Message


COMMAND = Command(
    'pxseu',
    syntax=None,
    description='Wysyła anonimową wiadomość przez API pxseu.',
    cooldown=5
)


def setup(cliffs):
    @cliffs.command('pxseu <message...>', command=COMMAND)
    async def command(m: Message, message):
        async with aiohttp.request(
                'POST', 'https://www.pxseu.com/api/v2/sendMessage',
                json={'message': message, 'user': m.author.id},
                headers={'Authorization': 'Bearer ' + getenv('PXSEU_MESSAGE_TOKEN')},
                timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            if r.status == 200:
                await m.success('good')
            else:
                await m.error(clean_content((await r.json())['message']))