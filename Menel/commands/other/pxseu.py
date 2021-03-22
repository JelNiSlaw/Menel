from os import getenv

import aiohttp

from ...functions import clean_content
from ...objects import Category, Command, Message


COMMAND = Command(
    'pxseu',
    syntax=None,
    description='Wysyła anonimową wiadomość przez API pxseu.',
    category=Category.OTHER,
    cooldown=5
)


def setup(cliffs):
    @cliffs.command('pxseu [(name|nick) <name>] <message...>', command=COMMAND)
    async def command(m: Message, message, name=None):
        async with aiohttp.request(
                'POST', 'https://www.pxseu.com/api/v2/sendMessage',
                json={'name': name, 'message': message, 'user': m.author.id},
                headers={'Authorization': 'Bearer ' + getenv('PXSEU_MESSAGE_TOKEN')},
                timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            if r.status == 200:
                await m.success('good')
            else:
                await m.error(clean_content((await r.json())['message']))