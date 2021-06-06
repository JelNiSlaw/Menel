import discord


def with_author(user: discord.User, **kwargs) -> discord.Embed:
    embed = discord.Embed(**kwargs)
    embed.set_author(name=str(user), icon_url=user.avatar.replace(256))

    return embed