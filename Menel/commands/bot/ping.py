import discord

from ...objects.message import Message


def setup(cliffs):
    @cliffs.command('ping', name='ping', cooldown=2)
    async def command(m: Message):
        message = await m.send('Pong!')

        delay = round((message.created_at.timestamp() - m.created_at.timestamp()) * 1000)

        try:
            await message.edit(content=f'Ping: {delay} ms')
        except discord.HTTPException:
            pass