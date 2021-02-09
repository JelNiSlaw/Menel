from time import perf_counter

import discord

from ...objects import bot, Category, Command, Message


COMMAND = Command(
    'ping',
    syntax=None,
    description='Sprawdza opóźnienie wysyłania wiadomości bota.',
    category=Category.BOT,
    cooldown=2,
)


def setup(cliffs):
    @cliffs.command('ping', command=COMMAND)
    async def command(m: Message):
        start = perf_counter()
        message = await m.send('Pong!')
        stop = perf_counter()

        embed = discord.Embed(
            description=f'Ogólne opóźnienie wiadomości: '
                        f'{round((message.created_at.timestamp() - m.created_at.timestamp()) * 1000)} ms\n'
                        f'Czas wysyłania wiadomości: {round((stop - start) * 1000)} ms\n'
                        f'Opóźnienie WebSocket: {round(bot.latency * 1000)} ms',
            colour=discord.Colour.blurple()
        )

        try:
            await message.edit(content=None, embed=embed)
        except discord.HTTPException:
            pass