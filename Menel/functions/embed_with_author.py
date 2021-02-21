import discord


def embed_with_author(user: discord.User, embed: discord.Embed = None) -> discord.Embed:
    if embed is None:
        embed = discord.Embed()

    embed.set_author(name=str(user), icon_url=str(user.avatar_url_as(size=256)))

    return embed