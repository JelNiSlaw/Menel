from datetime import timedelta

import discord

from ...objects import Category, Command, Message, snipes


COMMAND = Command(
    'snipe',
    syntax=None,
    description='Pokazuje usunięte lub edytowane wiadomości.',
    category=Category.UTILS,
    cooldown=1
)


def setup(cliffs):
    @cliffs.command('(snipe|editsnipe|botsnipe|boteditsnipe):mode', command=COMMAND)
    async def command(m: Message, mode):
        snipe = (snipes.delete, snipes.edit, snipes.botdelete, snipes.botedit)[mode].get(m.channel.id, (None, None))

        snipe, time = snipe

        if not snipe or time + timedelta(minutes=30) < discord.utils.utcnow():
            await m.error(f'Nie znalazłem żadnej {("usuniętej", "edytowanej")[mode % 2]} wiadomości.')
            return

        embed = discord.Embed(description=snipe.content, colour=snipe.author.colour, timestamp=time)
        embed.set_author(name=str(snipe.author), icon_url=snipe.author.avatar.replace(size=256))

        await m.send(embed=embed)