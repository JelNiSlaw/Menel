import asyncio
import io
import json
import math
import zipfile
from collections import Counter
from typing import Union

import discord
from discord.ext import commands

from ..bot import Menel
from ..utils import embeds, markdown
from ..utils.context import Context
from ..utils.misc import Timer
from ..utils.text_tools import escape, user_input


def oauth2_link(client_id: int, permissions: int) -> str:
    return discord.utils.oauth_url(
        client_id=str(client_id), permissions=discord.Permissions(permissions), scopes=("bot", "applications.commands")
    )


async def send_json(ctx: Context, data: dict, filename_id: str) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if len(text) <= 4000:
        await ctx.embed(markdown.codeblock(text, "json", escape=False))
    else:
        await ctx.send(file=discord.File(io.BytesIO(text.encode()), f"{filename_id}.json"))


class DiscordUtilities(commands.Cog, name="Discord Utilities"):
    def __init__(self, bot: Menel):
        self.bot = bot

    @commands.command(aliases=["av"])
    async def avatar(self, ctx: Context, *, user: Union[discord.Member, discord.User] = None):
        """Wysyła avatar użytkownika"""
        if user is None:
            user = ctx.author

        avatars: list[discord.Asset] = []
        message_embeds: list[discord.Embed] = []

        if (avatar := user.avatar) is not None:
            avatars.append(avatar)
        else:
            message_embeds.append(
                embeds.with_author(user, description=f"Użytkownik posiada [domyślny avatar]({user.default_avatar})")
            )
        if isinstance(user, discord.Member) and (guild_avatar := user.guild_avatar) is not None:
            avatars.append(guild_avatar)

        for avatar in avatars:
            formats = {"png": "PNG", "webp": "WebP", "jpeg": "JPEG"}
            if avatar.is_animated():
                formats.update({"gif": "GIF"})

            avatar = avatar.with_size(4096)

            embed = embeds.with_author(
                user,
                description=" ".join(
                    f"[{name}]({avatar.with_format(format)})" for format, name in formats.items()  # type: ignore
                ),
            )
            embed.set_image(url=str(avatar))
            message_embeds.append(embed)

        await ctx.send(embeds=message_embeds)

    @commands.command("name-history", aliases=["namehistory", "names", "nick-history", "nickhistory", "nicks"])
    async def name_history(self, ctx: Context, user: discord.User = None, *, page: int = 1):
        """Pokazuje historię nazw wybranego użytkownika"""
        user = user or ctx.author  # type: ignore
        if page <= 0:
            await ctx.error("Numer strony musi być dodatni")
            return

        names = await ctx.db.get_name_history(user.id)
        if not names:
            await ctx.error("Nie znam historii nazw tego użytkownika")
            return

        pages = math.ceil(len(names) / 16)
        if page > pages:
            await ctx.error(f"Maksymalny numer strony to {pages}")
            return

        names = names[::-1][(page - 1) * 16 : page * 16]
        embed = embeds.with_author(user, description="\n".join(escape(name) for name in names))
        embed.set_footer(text=f"Strona {page} z {pages}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["ban-reason", "baninfo", "ban-info"])
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def banreason(self, ctx: Context, *, user: discord.User):
        """Wyświetla powód bana"""
        try:
            ban = await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            await ctx.error(f"{escape(str(user))} nie jest zbanowany na tym serwerze")
            return

        embed = embeds.with_author(ban.user)
        reason = ban.reason
        embed.add_field(name="Powód bana", value=escape(reason) if reason else "Nie podano powodu", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["oauth2", "oauth"])
    async def invite(self, ctx: Context, *bots: Union[discord.User, discord.Object]):
        """
        Tworzy link autoryzacji bota
        `bots`: wzmianki lub ID botów
        """
        bots = discord.utils._unique(bots)  # type: ignore

        if not bots or len(bots) == 1 and bots[0] == ctx.bot.user:
            await ctx.embed(
                f"[Zaproś mnie na swój serwer]({oauth2_link(ctx.bot.user.id, 686947414)})\n"
                f"[Zaproś mnie na swój serwer z uprawnieniami administratora]({oauth2_link(ctx.bot.user.id, 8)})\n"
                f"[Zaproś mnie na swój serwer bez dodatkowych uprawnień]({oauth2_link(ctx.bot.user.id, 0)})"
            )
            return

        links = []
        for bot in bots[:8]:
            if isinstance(bot, discord.User):
                if not bot.bot:
                    await ctx.error(f"{user_input(str(bot))} nie jest botem")
                    return
                links.append(f"[Link zaproszenia {markdown.bold(escape(bot.name))}]({oauth2_link(bot.id, 0)})")
            else:
                links.append(f"[Link zaproszenia {markdown.bold(bot.id)}]({oauth2_link(bot.id, 0)})")

        if len(bots) > 8:
            links.append("…")

        await ctx.embed("\n".join(links))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def zipemojis(self, ctx: Context):
        """Wysyła serwerowe emoji w formacie pliku zip"""
        emojis = await ctx.guild.fetch_emojis()
        if not emojis:
            await ctx.error("Na tym serwerze nie ma żadnych emoji")
            return

        async with ctx.channel.typing():
            with Timer() as download_timer:
                emoji_data = await asyncio.gather(*(e.read() for e in emojis))
            file = io.BytesIO()
            name_counter = Counter()
            with Timer() as zip_timer:
                with zipfile.ZipFile(file, "w") as zip_file:
                    for emoji, data in zip(emojis, emoji_data):
                        count = name_counter[(emoji.name, emoji.animated)]
                        name = f"{emoji.name}_{count + 1}" if count > 0 else emoji.name
                        name += ".gif" if emoji.animated else ".png"
                        name_counter[(emoji.name, emoji.animated)] += 1
                        zip_file.writestr(name, data)
            file.seek(0)
        await ctx.send(
            f"Pobrano w {download_timer.time * 1000:.0f} ms, spakowano w {zip_timer.time * 1000:.0f} ms",
            file=discord.File(file, f"emojis_{ctx.guild.id}.zip"),
        )

    @commands.group(aliases=["json"], invoke_without_command=True)
    async def raw(self, ctx: Context):
        """Wysyła różne obiekty jako JSON"""
        await ctx.send_help(ctx.command)

    @raw.command("message")
    async def raw_message(self, ctx: Context, *, message: discord.PartialMessage):
        """Wysyła informacje o wybranej wiadomości"""
        if ctx.guild:
            if message.guild != ctx.guild:
                await ctx.error("Możesz wybrać jedynie wiadomość na tym serwerze")
                return
        elif message.channel != ctx.channel:
            await ctx.error("Możesz wybrać jedynie wiadomość na tym DM")
            return

        if not message.channel.permissions_for(ctx.author).read_message_history:
            raise commands.MissingPermissions(["read_message_history"])

        try:
            data = await ctx.bot.http.get_message(message.channel.id, message.id)
        except discord.NotFound:
            raise commands.MessageNotFound(str(message.id))

        await send_json(ctx, data, f"message_{message.id}")  # type: ignore

    @raw.command("member")
    async def raw_member(self, ctx: Context, *, member: discord.Member):
        """Wysyła informacje o wybranym członku"""
        data = await ctx.bot.http.get_member(ctx.guild.id, member.id)
        await send_json(ctx, data, f"member_{member.id}")  # type: ignore

    @raw.command("user")
    async def raw_user(self, ctx: Context, *, user: discord.User):
        """Wysyła informacje o wybranym użytkowniku"""
        data = await ctx.bot.http.get_user(user.id)
        await send_json(ctx, data, f"user_{user.id}")  # type: ignore

    @raw.command("channel")
    async def raw_channel(self, ctx: Context, *, channel: discord.abc.GuildChannel):
        """Wysyła informacje o wybranym kanale"""
        data = await ctx.bot.http.get_channel(channel.id)
        await send_json(ctx, data, f"channel_{channel.id}")  # type: ignore

    @raw.command("guild")
    async def raw_guild(self, ctx: Context):
        """Wysyła informacje o serwerze"""
        data = await ctx.bot.http.get_guild(ctx.guild.id)
        await send_json(ctx, data, f"guild_{ctx.guild.id}")  # type: ignore

    @raw.command("roles")
    async def raw_roles(self, ctx: Context):
        """Wysyła informacje o wszystkich rolach"""
        data = await ctx.bot.http.get_roles(ctx.guild.id)
        await send_json(ctx, data, f"roles_{ctx.guild.id}")  # type: ignore

    @raw.command("emoji")
    async def raw_emoji(self, ctx: Context, *, emoji: discord.Emoji):
        """Wysyła informacje o wybranym emoji"""
        data = await ctx.bot.http.get_custom_emoji(emoji.guild_id, emoji.id)
        await send_json(ctx, data, f"emoji_{emoji.id}")  # type: ignore

    @raw.command("emojis")
    async def raw_emojis(self, ctx: Context):
        """Wysyła informacje o wszystkich emoji"""
        data = await ctx.bot.http.get_all_custom_emojis(ctx.guild.id)
        await send_json(ctx, data, f"emojis_{ctx.guild.id}")  # type: ignore

    @raw.command("invite")
    async def raw_invite(self, ctx: Context, *, invite: discord.Invite):
        """Wysyła informacje o wybranym zaproszeniu"""
        data = await ctx.bot.http.get_invite(invite.code)
        await send_json(ctx, data, f"invite_{invite.id}")  # type: ignore

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if (before.name, before.discriminator) != (after.name, after.discriminator):
            await self.bot.db.add_name_history(after.id, str(before))


def setup(bot: Menel):
    bot.add_cog(DiscordUtilities(bot))
