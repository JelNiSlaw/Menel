from datetime import datetime
from math import ceil

from discord import Colour, Embed

from ...functions import plural_time
from ...objects import Category, Command, cooldowns, Message


COMMAND = Command(
    'cooldowns',
    syntax=None,
    description='Pokazuje obecne spowolnienia komend.',
    category=Category.OTHER,
    cooldown=2
)


def setup(cliffs):
    @cliffs.command('cooldowns', command=COMMAND)
    async def command(m: Message):
        if not cooldowns.cooldowns[m.author.id]:
            await m.send('Nie masz żadnych spowolnień.')
            return

        cooldown_list = set()
        for name, time in list(cooldowns.cooldowns[m.author.id].items())[:10]:
            cooldown_list.add(f'{name}: {plural_time(ceil(time - datetime.utcnow().timestamp()))}')

        await m.send(embed=Embed(
            title='Twoje obecne spowolnienia',
            description='\n'.join(cooldown_list),
            colour=Colour.blurple())
        )