from typing import Optional, Union

import discord
from discord.ext import commands

from ..utils import embeds
from ..utils.context import Context
from ..utils.formatting import bold
from ..utils.text_tools import clean_content, user_input


def oauth2_link(client_id: int, permissions: int) -> str:
    return discord.utils.oauth_url(
        client_id=str(client_id),
        permissions=discord.Permissions(permissions),
        scopes=('bot', 'applications.commands')
    )


class DiscordUtilities(commands.Cog, name='Discord Utilities'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['av'])
    async def avatar(self, ctx: Context, user: Optional[discord.User]):
        """Wysyła avatar użytkownika"""
        if not user:
            user = ctx.author

        embed = embeds.with_author(user)
        embed.description = ' '.join(f'[{fmt}]({user.avatar.replace(4096, fmt)})' for fmt in ('png', 'webp', 'jpeg'))
        embed.set_image(url=str(user.avatar.replace(4096)))
        await ctx.send(embed=embed)

    @commands.command(aliases=['name-history', 'namehistory', 'names', 'nick-history', 'nickhistory', 'nicks'])
    async def name_history(self, ctx: Context, *, user: discord.User):
        names = await ctx.db.get_name_history(user.id)
        if not names:
            await ctx.error('Nie znam historii nazw tego użytkownika')
            return

        await ctx.embed('\n'.join(clean_content(name) for name in names))

    @commands.command(aliases=['ban-reason', 'baninfo', 'ban-info'])
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def banreason(self, ctx: Context, *, user: discord.User):
        """Wyświetla powód bana"""
        try:
            ban = await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await ctx.error(f'{clean_content(str(user))} nie jest zbanowany na tym serwerze')
            return

        embed = embeds.with_author(ban.user)
        embed.add_field(name='Powód bana', value=clean_content(ban.reason), inline=False)
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
            await ctx.embed(
                f'[Zaproś mnie na swój serwer]({oauth2_link(ctx.bot.user.id, 686947414)})\n'
                f'[Zaproś mnie na swój serwer z uprawnieniami administratora]({oauth2_link(ctx.bot.user.id, 8)})\n'
                f'[Zaproś mnie na swój serwer bez dodatkowych uprawnień]({oauth2_link(ctx.bot.user.id, 0)})'
            )
            return

        links = []
        for bot in bots[:8]:
            if isinstance(bot, discord.User):
                if not bot.bot:
                    await ctx.error(f'{user_input(str(bot))} nie jest botem')
                    return
                links.append(f'[Link zaproszenia {bold(clean_content(bot.name))}]({oauth2_link(bot.id, 0)})')
            else:
                links.append(f'[Link zaproszenia {bold(bot.id)}]({oauth2_link(bot.id, 0)})')

        if len(bots) > 8:
            links.append('…')

        await ctx.embed('\n'.join(links))

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if (before.name, before.discriminator) == (after.name, after.discriminator):
            return

        await self.bot.db.add_name_history(after.id, str(before))


def setup(bot):
    bot.add_cog(DiscordUtilities(bot))