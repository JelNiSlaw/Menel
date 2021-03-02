import discord

from ...functions import embed_with_author, get_user
from ...objects import Category, Command, Message
from ...strings import USER_NOT_FOUND


COMMAND = Command(
    'avatar',
    syntax=None,
    description='Pokazuje avatar wybranej osoby.',
    aliases=('av',),
    category=Category.DISCORD_UTILS,
    cooldown=2
)


def setup(cliffs):
    @cliffs.command('(avatar|av) [<user...>]', command=COMMAND)
    async def command(m: Message, user=None):
        if user:
            if not (user := await get_user(user, m.guild)):
                await m.error(USER_NOT_FOUND)
                return
        else:
            user = m.author

        embed = embed_with_author(user, discord.Embed(colour=discord.Colour.green()))

        embed.description = ' '.join(
            f'[{ftype}]({user.avatar_url_as(format=ftype, size=4096)})' for ftype in ('png', 'webp', 'jpeg')
        )

        embed.set_image(url=str(user.avatar_url_as(static_format='png', size=4096)))

        await m.send(embed=embed)