import discord


def with_author(user: discord.User, color: discord.Colour = discord.Colour.green(), **kwargs) -> discord.Embed:
    embed = discord.Embed(colour=color, **kwargs)
    embed.set_author(name=str(user), icon_url=user.avatar.replace(256))

    return embed