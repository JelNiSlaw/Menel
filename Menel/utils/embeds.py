import discord


def with_author(user: discord.User, color: discord.Color = discord.Color.green(), **kwargs) -> discord.Embed:
    embed = discord.Embed(color=color, **kwargs)
    embed.set_author(name=str(user), icon_url=user.avatar.replace(256))

    return embed