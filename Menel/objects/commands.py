from typing import Optional

import discord


class Command:
    def __init__(
            self,
            name: str,
            *,
            syntax: Optional[str],
            description: str,
            cooldown: Optional[int] = None,
            global_perms: int = 0,
            user_perms: discord.Permissions = discord.Permissions.none(),
            bot_perms: discord.Permissions = discord.Permissions.none()
    ):
        self.name = name
        self.syntax = syntax
        self.description = description
        self.cooldown = cooldown
        self.global_perms = global_perms
        self.user_perms = user_perms
        self.bot_perms = bot_perms


commands = {}