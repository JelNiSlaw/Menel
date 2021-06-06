from typing import Optional

import discord
from discord.ext import commands

from ..objects.context import Context
from ..utils import converters, embeds
from ..utils.text_tools import clean_content


class DiscordUtilities(commands.Cog):
    def __init__(self):
        self.OAUTH2_SCOPES = 'bot', 'applications.commands'

    def oauth2_link(self, client_id: int, permissions: int) -> str:
        return discord.utils.oauth_url(
            client_id=str(client_id),
            permissions=discord.Permissions(permissions),
            scopes=self.OAUTH2_SCOPES
        )

    @commands.command(aliases=['av'])
    async def avatar(self, ctx: Context, user: Optional[discord.User]):
        if not user:
            user = ctx.author

        embed = embeds.with_author(user, colour=discord.Colour.green())
        embed.description = ' '.join(f'[{fmt}]({user.avatar.replace(4096, fmt)})' for fmt in ('png', 'webp', 'jpeg'))
        embed.set_image(url=str(user.avatar.replace(4096)))
        await ctx.send(embed=embed)

    @commands.command(aliases=['oauth2', 'oauth'])
    async def invite(self, ctx: Context, bot: Optional[converters.Bot]):
        if not bot:
            bot = ctx.bot.user

        if bot != ctx.bot.user:
            await ctx.info(f'[Link zaproszenia {clean_content(bot.name)}]({self.oauth2_link(bot.id, 0)})')
        else:
            await ctx.info(
                f'[Zaproś mnie na swój serwer]({self.oauth2_link(ctx.bot.user.id, 686947414)})\n'
                f'[Zaproś mnie na swój serwer z uprawnieniami administratora]({self.oauth2_link(ctx.bot.user.id, 8)})\n'
                f'[Zaproś mnie na swój serwer bez dodatkowych uprawnień]({self.oauth2_link(ctx.bot.user.id, 0)})'
            )


def setup(bot):
    bot.add_cog(DiscordUtilities())