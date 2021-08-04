from dataclasses import dataclass

import validators
from discord.ext import commands

from ..resources.languages import LANGCODES, LANGUAGES
from ..utils.context import Context
from ..utils.errors import BadLanguage, BadNumber


@dataclass
class ClampedNumber(commands.Converter[int]):
    min_value: int
    max_value: int

    async def convert(self, ctx: Context, argument: str) -> int:
        try:
            value = int(argument)
        except ValueError:
            raise commands.BadArgument()

        if value < self.min_value:
            raise BadNumber("Liczba", "mniejsza", self.min_value)
        if value > self.max_value:
            raise BadNumber("Liczba", "większa", self.max_value)

        return value

    def __call__(self):
        pass

    def __hash__(self):
        return hash((self.min_value, self.max_value))


class URL(commands.Converter[str]):
    async def convert(self, ctx: Context, argument: str) -> str:
        if argument.startswith("<") and argument.endswith(">"):
            argument = argument[1:-1]

        if not validators.url(argument):  # type: ignore
            raise commands.BadArgument("nieprawidłowy adres URL")

        return argument


class LanguageConverter(commands.Converter[str]):
    async def convert(self, ctx: Context, argument: str) -> str:
        argument = argument.lower()
        if argument != "auto" and argument not in LANGUAGES:
            if argument in LANGCODES:
                argument = LANGCODES[argument]
            else:
                raise BadLanguage(argument)

        return argument
