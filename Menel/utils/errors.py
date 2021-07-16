from dataclasses import dataclass
from typing import Optional

from discord.ext import commands

from ..utils.text_tools import plural


@dataclass
class BadNumber(commands.BadArgument):
    name: str
    problem: str
    value: int


class BadURL(commands.BadArgument):
    pass


@dataclass
class BadLanguage(commands.BadArgument):
    argument: str


class BadAttachmentCount(commands.CheckFailure):
    def __init__(self, expected: Optional[int]):
        text = 'Ta komenda wymaga załączenia '
        if expected is not None:
            text += plural(expected, 'pliku', 'plików', 'plików')
        else:
            text += 'przynajmniej jednego pliku'

        super().__init__(text)


@dataclass
class BadAttachmentType(commands.CheckFailure):
    type: str


@dataclass
class ImgurUploadError(Exception):
    code: int
    message: str