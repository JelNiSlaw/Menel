import discord

from ...functions import clean_content, get_user
from ...objects import Category, Command, Message
from ...strings import ACCOUNT_NOT_FOUND


COMMAND = Command(
    'invite',
    syntax=None,
    description='Tworzy link zaproszenia dowolnego bota.',
    category=Category.DISCORD_UTILS,
    cooldown=2
)


def setup(cliffs):
    @cliffs.command('invite [<user...>]', command=COMMAND)
    async def command(m: Message, user=None):
        if user:
            user = await get_user(user, m.guild)

            if not user:
                await m.error(ACCOUNT_NOT_FOUND)
                return

            if not user.bot:
                await m.error('Mogę tworzyć jedynie zaproszenia botów.')
                return

            await m.info(
                f'[Link zaproszenia {clean_content(user.name)}]'
                f'({discord.utils.oauth_url(user.id, discord.Permissions.none(), m.guild)})'
            )
        else:
            base = 'https://del.dog/'
            await m.info(
                f'[Zaproś mnie na swój serwer]({base}Menel)\n'
                f'[Zaproś mnie na swój serwer z uprawnieniami administratora]({base}MenelA)\n'
                f'[Zaproś mnie na swój serwer bez dodatkowych uprawnień]({base}MenelNP)'
            )