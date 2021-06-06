from typing import Optional

from discord.ext import commands

from ..utils.text_tools import plural


class BadAttachmentCount(commands.CheckFailure):
    def __init__(self, expected: Optional[int]):
        text = 'Ta komenda wymaga załączenia '
        if expected is not None:
            text += plural(expected, 'pliku', 'plików', 'plików')
        else:
            text += 'przynajmniej jednego pliku'

        super().__init__(text)


class BadAttachmentType(commands.CheckFailure):
    def __init__(self):
        super().__init__(f'Nieprawidłowy typ załącznika')


class ImgurUploadError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f'{code}: {message}')


class BadLanguage(commands.BadArgument):
    def __init__(self):
        super().__init__('Podano nieprawiłowy język')