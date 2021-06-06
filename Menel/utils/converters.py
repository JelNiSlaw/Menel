import discord
import validators
from discord.ext import commands
from googletrans.constants import LANGCODES, LANGUAGES

from ..objects.context import Context
from ..utils.errors import BadLanguage


class Bot(commands.UserConverter):
    async def convert(self, ctx: Context, user: str) -> discord.User:
        user = await super().convert(ctx, user)
        if user.bot:
            return user
        else:
            raise commands.BadArgument('wybrany użytkownik musi być botem')


class URL(commands.Converter, str):
    async def convert(self, ctx: Context, url: str) -> str:
        if url.startswith('<') and url.endswith('>'):
            url = url[1:-1]

        if not validators.url(url):
            raise commands.BadArgument('nieprawidłowy adres URL')
        else:
            return url


class LanguageConverter(commands.Converter, str):
    async def convert(self, ctx: Context, language: str) -> str:
        language = language.lower()
        if language != 'auto' and language not in LANGUAGES:
            if language in LANGCODES:
                language = LANGCODES[language]
            else:
                raise BadLanguage()

        return language