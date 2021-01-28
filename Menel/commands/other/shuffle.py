import random

from ...objects.commands import Command
from ...objects.message import Message


COMMAND = Command(
    'shuffle',
    syntax=None,
    description='Losowo zmienia kolejność słów.',
    cooldown=2
)


def setup(cliffs):
    @cliffs.command('(shuffle|shuffle-text) <text...>', command=COMMAND)
    async def command(m: Message, text):
        text = text.split()
        random.shuffle(text)
        await m.send(' '.join(text))