import logging
from typing import Iterable

import discord
from discord.ext import commands

from .database import Database
from ..utils import embeds
from ..utils.text_tools import clean_content, location


log = logging.getLogger(__name__)


class Context(commands.Context):
    message: discord.Message
    db = Database()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time = self.message.edited_at or self.message.created_at

    async def send(
        self,
        *args,
        channel: discord.abc.Messageable = None,
        reply: bool = True,
        **kwargs
    ) -> discord.Message:
        if not channel:
            channel = self.channel

        if 'reference' not in kwargs and reply:
            kwargs['reference'] = self.message.to_reference(fail_if_not_exists=False)

        try:
            log.debug(f'Sending a message to {location(self.author, channel, self.guild)}')
            return await channel.send(*args, **kwargs)

        except discord.Forbidden as e:
            log.error(e)

        except discord.HTTPException as e:
            try:
                return await channel.send(
                    embed=discord.Embed(
                        description=clean_content(str(e), max_length=512, max_lines=4),
                        colour=discord.Colour.red()
                    )
                )
            except discord.HTTPException:
                log.error(e)

    async def _send_embed(self, desc: str, color: discord.Colour, **kwargs) -> discord.Message:
        embed = embeds.with_author(self.author, description=desc, colour=color)
        return await self.send(embed=embed, **kwargs)

    async def info(self, text: str, **kwargs) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.blurple(), **kwargs)

    async def success(self, text: str, **kwargs) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.green(), **kwargs)

    async def error(self, text: str, **kwargs) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.red(), **kwargs)

    async def add_reactions(self, emojis: Iterable[str]) -> None:
        for e in emojis:
            await self.message.add_reaction(e)

    async def react_or_send(self, emoji: str):
        permissions = self.my_permissions()
        if permissions.add_reactions and permissions.read_message_history:
            await self.message.add_reaction(emoji)
        else:
            await self.channel.send(emoji)

    async def report_exception(self, exception: Exception):
        embed = embeds.with_author(
            self.author,
            title='Wystąpił błąd!',
            colour=discord.Colour.red()
        )

        embed.add_field(name=type(exception).__name__, value=clean_content(str(exception)), inline=False)

        owner = self.guild.get_member(self.bot.owner_id)
        if self.guild and owner:
            text = owner.mention
            allowed_mentions = discord.AllowedMentions(users=True)
        else:
            text = None
            allowed_mentions = None

        await self.send(text, embed=embed, allowed_mentions=allowed_mentions)

    def my_permissions(self) -> discord.Permissions:
        return self.channel.permissions_for(self.me)

    def author_permissions(self) -> discord.Permissions:
        return self.channel.permissions_for(self.author)