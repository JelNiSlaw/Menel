import itertools
from typing import Mapping, Optional

import discord
from discord.ext import commands as dc_commands

from ..objects.context import Context
from ..utils.formatting import code
from ..utils.text_tools import user_input


def command_category(command: dc_commands.Command) -> str:
    cog = command.cog
    return cog.qualified_name if cog is not None else 'Bot'


def command_category_and_name(command: dc_commands.Command) -> tuple[str, str]:
    return command_category(command), command.qualified_name


def group_categories(commands: set[dc_commands.Command]) -> itertools.groupby:
    commands = sorted(filter(lambda c: not c.hidden, commands), key=command_category_and_name)
    return itertools.groupby(commands, key=command_category)


class HelpCommand(dc_commands.HelpCommand):
    context: Context
    remove_mentions = staticmethod(user_input)

    async def send_bot_help(self, mapping: Mapping[Optional[dc_commands.Cog], list[dc_commands.Command]]) -> None:
        ctx = self.context

        embed = discord.Embed(
            title='Lista komend',
            description=f'Użyj `{ctx.clean_prefix}help [command]`, '
                        f'aby otrzymać więcej informacji o komendzie lub kategorii\n'
                        f'Ustawione prefixy: {await ctx.get_prefixes_str()}',
            colour=discord.Colour.green()
        )

        for category, commands in group_categories(ctx.bot.commands):
            embed.add_field(name=category, value=' '.join(code(c.name) for c in commands), inline=False)

        await ctx.send(embed=embed)

    async def send_error_message(self, error: str) -> None:
        await self.context.error(error)

    def command_not_found(self, name: str) -> str:
        return f'Nie znaleziono komendy {name}'

    def subcommand_not_found(self, command: dc_commands.Command, name: str) -> str:
        if isinstance(command, dc_commands.Group):
            return f'Komenda **{command.qualified_name}** nie ma subkomendy o nazwie {name}'
        return f'Komenda **{command.qualified_name}** nie ma subkomend'