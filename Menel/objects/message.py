import logging
from datetime import datetime
from typing import Iterable

import discord

from .bot import bot
from ..functions import clean_content, embed_with_author


log = logging.getLogger(__name__)


class Message(discord.Message):
    def __init__(self, message: discord.Message):
        self.message = message
        self._created_at = message.created_at
        self.bot = bot


    def __getattr__(self, item):
        return self.message.__getattribute__(item)


    async def send(
        self,
        *args,
        channel: discord.abc.Messageable = None,
        reply: bool = True,
        **kwargs
    ) -> discord.Message:
        if not channel:
            channel = self.channel

        if not channel.permissions_for(self.guild.me).read_message_history:
            if 'reference' in kwargs:
                kwargs.pop('reference')

        elif reply:
            kwargs['reference'] = self.message.to_reference(fail_if_not_exists=False)

        try:
            log.debug(f'Sending a message to @{self.author} in #{channel} in {self.guild}')
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
        embed = discord.Embed(description=desc, colour=color)
        embed = embed_with_author(self.author, embed)
        return await self.send(embed=embed, **kwargs)


    async def info(self, text: str, **kwargs) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.blurple(), **kwargs)


    async def success(self, text: str, **kwargs) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.green(), **kwargs)


    async def error(self, text: str, **kwargs) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.red(), **kwargs)


    async def add_reactions(self, emojis: Iterable) -> None:
        for e in emojis:
            await self.add_reaction(e)


    @property
    def created_at(self):
        return self._created_at


    @created_at.setter
    def created_at(self, time: datetime):
        self._created_at = time