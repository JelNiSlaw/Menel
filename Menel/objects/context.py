import logging
import sys
import traceback
from typing import Iterable, TYPE_CHECKING

import discord
from discord.ext import commands

from ..utils import embeds
from ..utils.text_tools import clean_content, location


if TYPE_CHECKING:
    from httpx import AsyncClient
    from .bot import Menel
    from .database import Database

log = logging.getLogger(__name__)


class Context(commands.Context):
    message: discord.Message
    bot: 'Menel'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db: 'Database' = self.bot.db
        self.client: 'AsyncClient' = self.bot.client
        self.command_time = self.message.edited_at or self.message.created_at

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

        log.debug(f'Sending a message to {location(self.author, channel, self.guild)}')
        return await channel.send(*args, **kwargs)

    async def _send_embed(self, desc: str, color: discord.Colour, **kwargs) -> discord.Message:
        return await self.send(embed=embeds.with_author(self.author, description=desc, colour=color), **kwargs)

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
            await self.send(emoji)

    async def report_exception(self, exception: Exception) -> discord.Message:
        log.error(exception)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

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

        return await self.send(text, embed=embed, allowed_mentions=allowed_mentions)

    def my_permissions(self) -> discord.Permissions:
        return self.channel.permissions_for(self.me)

    def author_permissions(self) -> discord.Permissions:
        return self.channel.permissions_for(self.author)