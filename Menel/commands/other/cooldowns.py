from datetime import datetime
from math import ceil

from discord import Colour, Embed

from ...functions.plural_time import plural_time
from ...objects.commands import Command
from ...objects.cooldowns import cooldowns
from ...objects.message import Message


COMMAND = Command(
    'cooldowns',
    syntax=None,
    description='Pokazuje obecne spowolnienia komend.',
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