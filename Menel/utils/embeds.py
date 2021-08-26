from typing import Union

import discord


def with_author(
    user: Union[discord.Member, discord.User], *, color: discord.Color = discord.Color.green(), **kwargs
) -> discord.Embed:
    return discord.Embed(color=color, **kwargs).set_author(name=str(user), icon_url=user.avatar.with_size(4096))
