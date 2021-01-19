import random

from ...objects.message import Message


def setup(cliffs):
    @cliffs.command('(shuffle|shuffle-text) <text...>', name='shuffle', cooldown=2)
    async def command(m: Message, text):
        text = text.split()
        random.shuffle(text)
        await m.send(' '.join(text))