from datetime import datetime, timedelta

import discord

from ...objects.message import Message
from ...objects.snipes import snipes


def setup(cliffs):
    @cliffs.command('(snipe|editsnipe|botsnipe|boteditsnipe):mode', name='snipe', cooldown=1)
    async def command(m: Message, mode):
        snipe = (snipes.delete, snipes.edit, snipes.botdelete, snipes.botedit)[mode].get(m.channel.id, (None, None))

        snipe, time = snipe

        if not snipe or time + timedelta(minutes=30) < datetime.utcnow():
            await m.error(f'Nie znalazłem żadnej {("usuniętej", "edytowanej")[mode % 2]} wiadomości.')
            return

        embed = discord.Embed(description=snipe.content, colour=snipe.author.colour, timestamp=time)
        embed.set_author(name=str(snipe.author), icon_url=snipe.author.avatar_url_as(size=256))

        await m.send(embed=embed)