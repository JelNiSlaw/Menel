from enum import Enum
from typing import Optional

import discord


class Category(Enum):
    BOT = 'Bot'
    UTILS = 'Narzędzia'
    MODERATION = 'Moderacja'
    IMAGE = 'Obrazki'
    OTHER = 'Inne'
    OWNER = 'Deweloperskie'


class Command:
    def __init__(
            self,
            name: str,
            *,
            syntax: Optional[str],
            description: str,
            aliases: Optional[tuple] = None,
            category: Category,
            cooldown: Optional[int] = None,
            global_perms: int = 0,
            user_perms: Optional[discord.Permissions] = None,
            bot_perms: Optional[discord.Permissions] = None,
            hidden: bool = False
    ):
        self.name = name
        self.syntax = syntax
        self.description = description
        self.aliases = aliases
        self.category = category
        self.cooldown = cooldown
        self.global_perms = global_perms
        self.user_perms = user_perms
        self.bot_perms = bot_perms
        self.hidden = hidden


commands = {}