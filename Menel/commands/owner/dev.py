import ast
import traceback
from textwrap import indent
from time import perf_counter

import discord

from ...functions import get_user
from ...helpers import imperial
from ...objects import Category, Command, Message, bot
from ...resources.regexes import CODEBLOCK


COMMAND = Command(
    'dev',
    syntax=None,
    description='Wykonuje wpisany kod.',
    category=Category.OWNER,
    global_perms=5,
    hidden=True
)


def setup(cliffs):
    @cliffs.command('dev <code...>', command=COMMAND)
    async def command(m: Message, code):
        if match := CODEBLOCK.fullmatch(code):
            code = match.group('code')

        variables = {
            'm': m,
            'bot': bot,
            'get_user': get_user,
            'discord': discord
        }

        success = False
        start = None

        try:
            code = ast.parse('async def _eval():\n' + indent(code, ' ' * 2), filename='eval')
            # noinspection PyUnresolvedReferences
            insert_returns(code.body[0].body)
            exec(compile(code, filename='eval', mode='exec', optimize=2), variables, None)
            start = perf_counter()
            output = repr(await eval('_eval()', variables))
        except Exception:
            output = traceback.format_exc()
        else:
            success = True
        finally:
            finnish = perf_counter()

        if len(output) < 1024:
            output = f'```\n{output}\n```'
        else:
            paste = await imperial.create_document(output)
            output = paste.formatted_link

        embed = discord.Embed(colour=discord.Colour.green() if success else discord.Colour.red())
        embed.add_field(name='Output', value=output, inline=False)
        if start:
            embed.add_field(name='Time', value=f'{round((finnish - start) * 1000, 2)} ms', inline=False)

        await m.send(embed=embed)


# Function from https://gist.github.com/nitros12/2c3c265813121492655bc95aa54da6b9
def insert_returns(body) -> None:
    if len(body) <= 0:
        return

    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    elif isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    elif isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)