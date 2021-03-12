import unicodedata as ud

from ...functions import codeblock
from ...objects import Category, Command, Message


COMMAND = Command(
    'unicode',
    syntax=None,
    description='Podaje informacje o wpisanych znakach.',
    category=Category.UTILS,
    cooldown=3
)


def setup(cliffs):
    @cliffs.command('unicode <chars...>', command=COMMAND)
    async def command(m: Message, chars):
        output = []

        for c in chars[:16]:
            output.append(f'{c} – {"U+" + hex(ord(c))[2:].upper().zfill(4)} – {ud.name(c, "UNKNOWN CHARACTER")}')

        if len(chars) > 16:
            output.append('...')

        await m.send(codeblock('\n'.join(output)))