from datetime import datetime

import discord

from ..functions import embed_with_author


class Message(discord.Message):
    def __init__(self, message: discord.Message):
        self.message = message
        self._created_at = message.created_at


    def __getattr__(self, item):
        return self.message.__getattribute__(item)


    async def send(self, *args, reply: bool = True, **kwargs) -> discord.Message:
        if 'reference' in kwargs and not self.channel.permissions_for(self.guild.me).is_superset(
                discord.Permissions(read_message_history=True)
        ):
            kwargs.pop('reference')
        elif reply:
            kwargs['reference'] = self.message

        try:
            return await self.channel.send(*args, **kwargs)
        except discord.Forbidden:
            pass
        except discord.HTTPException as e:
            if e.code == 50035 and 'message_reference: Unknown message' in e.text and 'reference' in kwargs:
                kwargs.pop('reference')
                await self.send(*args, **kwargs)
            else:
                try:
                    return await self.channel.send(embed=discord.Embed(description=str(e), colour=discord.Colour.red()))
                except discord.HTTPException:
                    pass


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


    @property
    def created_at(self):
        return self._created_at


    @created_at.setter
    def created_at(self, time: datetime):
        self._created_at = time