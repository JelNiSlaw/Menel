from textwrap import indent
from time import perf_counter

import discord

from ...functions.cut_long_text import cut_long_text
from ...objects.commands import Command
from ...objects.message import Message


COMMAND = Command(
    'eval',
    syntax=None,
    description='Wykonuje wpisany kod.',
    global_perms=5
)


def setup(cliffs):
    @cliffs.command('eval <code...>', command=COMMAND)
    async def command(m: Message, code):
        if '\n' not in code:
            code = ' ' * 2 + f'return {code}'
        else:
            code = indent(code, ' ' * 2)

        success = False
        start = perf_counter()

        try:
            exec(f'async def to_eval(m):\n{code}')
            output = repr(await eval('to_eval(m)'))
        except Exception as e:
            output = str(e)
        else:
            success = True
        finally:
            finnish = perf_counter()

        embed = discord.Embed(colour=discord.Colour.green() if success else discord.Colour.red())
        embed.add_field(name='Output', value=f'```\n{cut_long_text(output, 1000)}\n```', inline=False)
        embed.add_field(name='Time', value=f'{round((finnish - start) * 1000, 2)} ms', inline=False)

        await m.send(embed=embed)