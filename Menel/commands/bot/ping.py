import discord

from ...objects import Command, Message


COMMAND = Command(
    'ping',
    syntax=None,
    description='Sprawdza opóźnienie wysyłania wiadomości bota.',
    cooldown=2,
)


def setup(cliffs):
    @cliffs.command('ping', command=COMMAND)
    async def command(m: Message):
        message = await m.send('Pong!')

        delay = round((message.created_at.timestamp() - m.created_at.timestamp()) * 1000)

        result = f'Ping: {delay} ms'

        try:
            await message.edit(content=result)
        except discord.HTTPException:
            await m.send(result)