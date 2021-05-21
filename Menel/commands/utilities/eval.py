import re

import aiohttp
import discord

from ...functions import clean_content, codeblock
from ...objects import Category, Command, Message
from ...resources.regexes import CODEBLOCK


COMMAND = Command(
    'eval',
    syntax=None,
    description='Wykonuje dowolny kod.',
    aliases=('run',),
    category=Category.UTILS,
    cooldown=3
)


def setup(cliffs):
    @cliffs.command('(eval|run) <code...>', command=COMMAND)
    async def command(m: Message, code):
        match = re.fullmatch(r'(?P<lang>\w*)\s*' + CODEBLOCK.pattern, code, re.DOTALL)

        if not match:
            await m.error('Umieść kod w bloku kodu:\n\\`\\`\\`język\nkod\n\\`\\`\\`')
            return

        language = match.group('lang') or match.group('language')
        if not language:
            await m.error('Podaj język kodu.')
            return

        code = match.group('code')
        if not code.strip():
            await m.error('Podaj kod do wykonania.')
            return

        async with m.channel.typing():
            async with aiohttp.request(
                    'POST', 'https://emkc.org/api/v1/piston/execute',
                    json={
                        'language': language,
                        'source': code
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                json = await r.json()
            if r.status != 200:
                await m.error(json.get('message', 'Nieznany błąd.'))
                return

            output = [codeblock(clean_content(json[out], False, False, max_length=512, max_lines=16))
                for out in ('stdout', 'stderr') if json[out].strip()]

            embed = discord.Embed(
                description=('\n'.join(output) if output else
                             'Twój kod nie zwrócił żadnego wyniku.') +
                            f'\n{json["language"]} {json["version"]}\n'
                            f'Powered by [Piston](https://github.com/engineer-man/piston).',
                colour=discord.Colour.green() if not json['stderr'].strip() else discord.Colour.red()
            )

        await m.send(embed=embed)