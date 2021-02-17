import random

import aiohttp

from ...functions import clean_content
from ...objects import Category, Command, Message


COMMAND = Command(
    'generate-sentence',
    syntax=None,
    description='Generuje losowe zdanie.',
    category=Category.OTHER,
    cooldown=2,
)

words = {}

variants = (
    ('characterTraits', 'anatomy'),
    ('characterTraits', 'colors', 'anatomy'),
    ('characterTraits', 'famousPeople'),
    ('emotions', 'adjectivePhrases'),
    ('anatomy', 'adjectivePhrases'),
    ('freestyle',) * 3,
    ('colors', 'adjectives', 'nouns'),
    ('adjectives', 'occupations')
)


def setup(cliffs):
    @cliffs.command('generate-sentence|generate sentence|zdanie', command=COMMAND)
    async def command(m: Message):
        global words

        if not words:
            async with aiohttp.request(
                    'GET', 'https://muldu.com/api/words',
                    headers={'Referer': 'https://muldu.com/pl/generator/slowa'},
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                words = await r.json()

        sentence = (random.choice(words[category]) for category in random.choice(variants))

        await m.send(clean_content(' '.join(sentence).lower()))