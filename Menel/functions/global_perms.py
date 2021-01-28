import discord

from ..objects.bot import bot
from ..objects.message import Message


def global_perms(m: Message) -> int:
    if m.author.id == bot.owner:
        return 5  # bot owner
    elif m.author == m.guild.owner:
        return 4  # guild owner
    elif m.channel.permissions_for(m.author).is_superset(discord.Permissions(8)):
        return 3  # admin
    elif m.channel.permissions_for(m.author).is_superset(discord.Permissions(32)):
        return 2  # manage server
    else:
        return 0  # normal user