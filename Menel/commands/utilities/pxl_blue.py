from ...helpers import pxl_blue
from ...objects import Category, Command, Message


COMMAND = Command(
    'pxl',
    syntax=None,
    description='Przesyła plik na pxl.blue.',
    aliases=('pxl.blue',),
    category=Category.UTILS,
    cooldown=10,
    hidden=True
)


def setup(cliffs):
    @cliffs.command('pxl.blue|pxl', command=COMMAND)
    async def command(m: Message):
        if not m.attachments:
            await m.error('Załącz plik do przesłania')
            return

        a = m.attachments[0]
        image = await pxl_blue.upload(await a.read(), a.filename, content_type=a.content_type)
        await m.success(f'Plik przesłano na {image.raw_url}')