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

SCOPES = ('bot', 'applications.commands')


def setup(cliffs):
    @cliffs.command('(invite|oauth) [<user...>]', command=COMMAND)
    async def command(m: Message, bot=None):
        if bot:
            bot = await get_user(bot, m.guild)

            if not bot:
                await m.error(ACCOUNT_NOT_FOUND)
                return

            if not bot.bot:
                await m.error('Mogę tworzyć jedynie zaproszenia botów.')
                return

            await m.info(f'[Link zaproszenia {clean_content(bot.name)}]({create_link(bot.id, 0)})')
        else:
            await m.info(
                f'[Zaproś mnie na swój serwer]({create_link(m.bot.user.id, 686947414)})\n'
                f'[Zaproś mnie na swój serwer z uprawnieniami administratora]({create_link(m.bot.user.id, 8)})\n'
                f'[Zaproś mnie na swój serwer bez dodatkowych uprawnień]({create_link(m.bot.user.id, 0)})'
            )


def create_link(client_id: int, permissions: int) -> str:
    return discord.utils.oauth_url(
        client_id=str(client_id),
        permissions=discord.Permissions(permissions),
        scopes=SCOPES
    )