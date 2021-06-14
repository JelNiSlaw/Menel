from typing import Optional, Union

import discord
from discord.ext import commands

from ..objects.context import Context
from ..utils import embeds
from ..utils.formatting import bold
from ..utils.text_tools import clean_content, user_input


def oauth2_link(client_id: int, permissions: int) -> str:
    return discord.utils.oauth_url(
        client_id=str(client_id),
        permissions=discord.Permissions(permissions),
        scopes=('bot', 'applications.commands')
    )


class DiscordUtilities(commands.Cog, name='Narzędzia Discord'):
    @commands.command(aliases=['av'])
    async def avatar(self, ctx: Context, user: Optional[discord.User]):
        """Wysyła avatar użytkownika"""
        if not user:
            user = ctx.author

        embed = embeds.with_author(user, colour=discord.Colour.green())
        embed.description = ' '.join(f'[{fmt}]({user.avatar.replace(4096, fmt)})' for fmt in ('png', 'webp', 'jpeg'))
        embed.set_image(url=str(user.avatar.replace(4096)))
        await ctx.send(embed=embed)

    @commands.command(aliases=['oauth2', 'oauth'])
    async def invite(self, ctx: Context, *bots: Union[discord.User, discord.Object]):
        """
        Tworzy link autoryzacji bota
        `bots`: wzmianki lub ID botów
        """

        # noinspection PyProtectedMember
        bots = discord.utils._unique(bots)

        if not bots or len(bots) == 1 and bots[0] == ctx.bot.user:
            await ctx.info(
                f'[Zaproś mnie na swój serwer]({oauth2_link(ctx.bot.user.id, 686947414)})\n'
                f'[Zaproś mnie na swój serwer z uprawnieniami administratora]({oauth2_link(ctx.bot.user.id, 8)})\n'
                f'[Zaproś mnie na swój serwer bez dodatkowych uprawnień]({oauth2_link(ctx.bot.user.id, 0)})'
            )
            return

        links = []
        for bot in bots[:16]:
            if isinstance(bot, discord.User):
                if not bot.bot:
                    await ctx.error(f'{user_input(str(bot))} nie jest botem')
                    return
                links.append(f'[Link zaproszenia {bold(clean_content(bot.name))}]({oauth2_link(bot.id, 0)})')
            else:
                links.append(f'[Link zaproszenia {bold(bot.id)}]({oauth2_link(bot.id, 0)})')

        if len(bots) > 16:
            links.append('…')

        await ctx.info('\n'.join(links))


def setup(bot):
    bot.add_cog(DiscordUtilities())