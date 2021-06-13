from typing import Optional, Union

import discord
from discord.ext import commands

from ..objects.context import Context
from ..utils import embeds
from ..utils.text_tools import clean_content


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
    async def invite(self, ctx: Context, bot: Optional[Union[discord.User, discord.Object]]):
        """
        Tworzy link autoryzacji bota
        `bot`: wzmianka lub ID bota
        """
        if not bot:
            bot = ctx.bot.user

        if bot.id != ctx.bot.user.id:
            if isinstance(bot, discord.User):
                if not bot.bot:
                    await ctx.error('Wybrany użytkownik musi być botem')
                    return
                text = f'[Link zaproszenia {clean_content(bot.name)}]({oauth2_link(bot.id, 0)})'
            else:
                text = f'[Link zaproszenia]({oauth2_link(bot.id, 0)})\n' \
                       f'Nie znaleziono użytkownika o takim ID, więc link może nie być prawidłowy'
            await ctx.info(text)
        else:
            await ctx.info(
                f'[Zaproś mnie na swój serwer]({oauth2_link(ctx.bot.user.id, 686947414)})\n'
                f'[Zaproś mnie na swój serwer z uprawnieniami administratora]({oauth2_link(ctx.bot.user.id, 8)})\n'
                f'[Zaproś mnie na swój serwer bez dodatkowych uprawnień]({oauth2_link(ctx.bot.user.id, 0)})'
            )


def setup(bot):
    bot.add_cog(DiscordUtilities())