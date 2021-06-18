import logging
import sys
import traceback
from typing import Iterable, Optional, TYPE_CHECKING, Union

import discord
import httpx
from discord.ext import commands

from ..utils import embeds
from ..utils.formatting import code
from ..utils.text_tools import clean_content, location


if TYPE_CHECKING:
    from ..bot import Menel
    from .database import Database

log = logging.getLogger(__name__)


class Context(commands.Context):
    message: discord.Message
    author: Union[discord.Member, discord.User]
    guild: Optional[discord.Guild]
    bot: 'Menel'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db: 'Database' = self.bot.db
        self.client: httpx.AsyncClient = self.bot.client
        self.command_time = self.message.edited_at or self.message.created_at

    async def send(
        self,
        *args,
        channel: discord.abc.Messageable = None,
        no_reply: bool = False,
        **kwargs
    ) -> discord.Message:
        if not channel:
            channel = self.channel

        if 'reference' not in kwargs and not no_reply:
            kwargs['reference'] = self.message.to_reference(fail_if_not_exists=False)

        log.debug(f'Sending a message to {location(self.author, channel, self.guild)}')
        return await channel.send(*args, **kwargs)

    async def embed(self, content: str, *, embed_kwargs: dict = None, **message_kwargs) -> discord.Message:
        return await self.send(
            embed=embeds.with_author(
                self.author,
                description=content,
                colour=discord.Colour.green(),
                **(embed_kwargs or {})
            ),
            **message_kwargs
        )

    async def error(self, content: str, *, embed_kwargs: dict = None, **message_kwargs) -> discord.Message:
        return await self.send(
            embed=embeds.with_author(
                self.author,
                description=content,
                colour=discord.Colour.red(),
                **(embed_kwargs or {})
            ),
            **message_kwargs
        )

    async def ok_hand(self):
        await self.send('\N{OK HAND SIGN}')

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

    @property
    def clean_prefix(self):
        if self.prefix in self.bot.prefix_base:
            return f'@{self.bot.user.name} '
        return self.prefix

    async def get_prefixes_str(self, *, join: str = ' ') -> str:
        prefixes = await self.db.get_prefixes(self.guild.id)
        return join.join([code('@' + self.bot.user.name)] + list(map(code, prefixes)))