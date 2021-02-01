import discord
import humanize

from ...functions.clean_content import clean_content
from ...functions.get_user import get_user
from ...objects.commands import Command
from ...objects.database import database
from ...objects.message import Message


COMMAND = Command(
    'lastseen',
    syntax=None,
    description='Pokazuję ostatnią datę kiedy wybrana osoba była online.',
    cooldown=2
)

humanize.activate('pl_PL')

TYPES = {
    discord.Status.online.value: 'online',
    discord.Status.idle.value: 'zaraz wracam',
    discord.Status.dnd.value: 'nie przeszkadzać',
    discord.Status.offline.value: 'offline'
}

DEVICES = ('na komputerze', 'w przeglądarce', 'na telefonie')


def setup(cliffs):
    @cliffs.command('lastseen <user...>', command=COMMAND)
    async def command(m: Message, user):
        user = await get_user(user, m.guild)

        if not user:
            await m.error('Nie znalazłem tego użytkownika.')
            return

        document = await database.lastseen.find_one(user.id)

        if not document:
            await m.error(f'Nie znam ostatniej daty, kiedy {clean_content(user.name)} był online.')
            return

        if isinstance(user, discord.Member) and user.status != discord.Status.offline:
            time = 'teraz'
        else:
            time = m.created_at - document["time"]
            time = humanize.naturaldelta(time, months=False) + ' temu'

        devices = [device for device, value in zip(DEVICES, document['devices']) if value]
        if devices:
            devices = ', ' + ', '.join(devices)
        else:
            devices = ''

        await m.success(
            f'{clean_content(user.name)}:\n'
            f'Ostatnia aktywność: {time}\n'
            f'Typ: {TYPES[document["status"]]}{devices}' +
            ('\nTen użytkownik nie znajduje się na tym serwerze, więc dane mogą nie być dokładne.'
             if not isinstance(user, discord.Member) else '')
        )