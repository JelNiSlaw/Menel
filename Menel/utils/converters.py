from dataclasses import dataclass

import validators
from discord.ext import commands
from googletrans.constants import LANGCODES, LANGUAGES

from ..utils.context import Context
from ..utils.errors import BadLanguage, BadNumber


@dataclass
class ClampedNumber(commands.Converter):
    min_value: int
    max_value: int

    async def convert(self, ctx: Context, argument: str) -> int:
        try:
            argument = int(argument)
        except ValueError:
            raise commands.BadArgument()

        if argument < self.min_value:
            raise BadNumber('Liczba', 'mniejsza', self.min_value)
        if argument > self.max_value:
            raise BadNumber('Liczba', 'większa', self.max_value)

        return argument


class URL(commands.Converter, str):
    async def convert(self, ctx: Context, argument: str) -> str:
        if argument.startswith('<') and argument.endswith('>'):
            argument = argument[1:-1]

        if not validators.url(argument):
            raise commands.BadArgument('nieprawidłowy adres URL')
        else:
            return argument


class LanguageConverter(commands.Converter, str):
    async def convert(self, ctx: Context, argument: str) -> str:
        argument = argument.lower()
        if argument != 'auto' and argument not in LANGUAGES:
            if argument in LANGCODES:
                argument = LANGCODES[argument]
            else:
                raise BadLanguage(argument)

        return argument