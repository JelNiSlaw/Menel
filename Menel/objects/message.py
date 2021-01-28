from datetime import datetime
from typing import Optional

import discord


class Message(discord.Message):
    def __init__(self, message: discord.Message):
        self.message = message
        self._created_at = message.created_at


    def __getattr__(self, item):
        return self.message.__getattribute__(item)


    async def send(self, *args, **kwargs) -> discord.Message:
        try:
            return await self.channel.send(*args, **kwargs)
        except discord.Forbidden:
            pass
        except discord.HTTPException as e:
            try:
                return await self.channel.send(embed=discord.Embed(description=str(e), colour=discord.Colour.red()))
            except discord.HTTPException:
                pass


    async def _send_embed(self, desc: str, color: discord.Colour,
            delete_after: Optional[int] = None) -> discord.Message:
        embed = discord.Embed(description=desc, colour=color)
        embed.set_author(name=str(self.author), icon_url=str(self.author.avatar_url_as(size=256)))
        return await self.send(embed=embed, delete_after=delete_after)


    async def info(self, text: str) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.blurple())


    async def success(self, text: str) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.green())


    async def error(self, text: str, delete_after: Optional[int] = None) -> discord.Message:
        return await self._send_embed(text, color=discord.Colour.red(), delete_after=delete_after)


    @property
    def created_at(self):
        return self._created_at


    @created_at.setter
    def created_at(self, time: datetime):
        self._created_at = time