from ...helpers import pxl_blue
from ...objects import Category, Command, Message


COMMAND = Command(
    'pxl',
    syntax=None,
    description='Przesyła plik na pxl.blue.',
    category=Category.OWNER,
    global_perms=5,
    hidden=True
)


def setup(cliffs):
    @cliffs.command('pxl', command=COMMAND)
    async def command(m: Message):
        if not m.attachments:
            await m.error('Załącz plik do przesłania')
            return

        attachment = m.attachments[0]
        image = await pxl_blue.upload(await attachment.read(), attachment.filename)
        await m.success(f'Plik przesłano na {image.raw_url}')