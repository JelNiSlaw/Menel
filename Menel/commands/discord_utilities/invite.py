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
    async def command(m: Message, bot=None):
        if bot:
            bot = await get_user(bot, m.guild)

            if not bot:
                await m.error(ACCOUNT_NOT_FOUND)
                return

            if not bot.bot:
                await m.error('Mogę tworzyć jedynie zaproszenia botów.')
                return

            link = discord.utils.oauth_url(
                client_id=bot.id,
                permissions=discord.Permissions.none(),
                guild=m.guild,
                scopes=('bot', 'applications.commands')
            )

            await m.info(f'[Link zaproszenia {clean_content(bot.name)}]({link})')
        else:
            base = 'https://del.dog/'
            await m.info(
                f'[Zaproś mnie na swój serwer]({base}Menel)\n'
                f'[Zaproś mnie na swój serwer z uprawnieniami administratora]({base}MenelA)\n'
                f'[Zaproś mnie na swój serwer bez dodatkowych uprawnień]({base}MenelNP)'
            )