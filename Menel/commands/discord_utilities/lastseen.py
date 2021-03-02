import discord
import humanize

from ...functions import clean_content, embed_with_author, get_user
from ...objects import Category, Command, Message, database
from ...strings import USER_NOT_FOUND


COMMAND = Command(
    'lastseen',
    syntax=None,
    description='Pokazuję ostatnią datę kiedy wybrana osoba była online.',
    aliases=('lastonline',),
    category=Category.UTILS,
    cooldown=2
)

humanize.activate('pl_PL')

STATUSES = {
    discord.Status.online.value: 'online',
    discord.Status.idle.value: 'zaraz wracam',
    discord.Status.dnd.value: 'nie przeszkadzać',
    discord.Status.offline.value: 'offline'
}

DEVICES = ('na komputerze', 'w przeglądarce', 'na telefonie')


def setup(cliffs):
    @cliffs.command('(lastseen|lastonline) [<user...>]', command=COMMAND)
    async def command(m: Message, user=None):
        if user:
            if not (user := await get_user(user, m.guild)):
                await m.error(USER_NOT_FOUND)
                return
        else:
            user = m.author

        if isinstance(user, discord.Member) and user.status != discord.Status.offline:
            time = 'teraz'
            status = user.status.value
            devices = (device for device, value in
                zip(DEVICES, (user.desktop_status, user.web_status, user.mobile_status)) if value)
        else:
            document = await database.lastseen.find_one(user.id)

            if not document:
                await m.error(f'Nie znam ostatniej daty, kiedy {clean_content(user.name)} był/a online.')
                return

            time = m.created_at - document["time"]
            time = humanize.naturaldelta(time, months=False) + ' temu'

            status = document["status"]

            devices = [device for device, value in zip(DEVICES, document['devices']) if value]

        status = STATUSES[status]
        devices = ', ' + ', '.join(devices)

        embed = embed_with_author(m.author, discord.Embed(colour=discord.Colour.blurple()))

        embed.description = (
                f'Ostatnia aktywność: {time}\n'
                f'Typ: ' + status + devices +
                ('\nTen użytkownik nie znajduje się na tym serwerze, więc dane mogą nie być dokładne.'
                 if not isinstance(user, discord.Member) else '')
        )

        await m.send(embed=embed)