import asyncio
import logging

import discord
from discord.ext import commands

from .formatting import bold, code
from .text_tools import clean_content, name_id
from ..objects.context import Context
from ..utils import errors


log = logging.getLogger(__name__)

SEND_EXCEPTIONS = (
    commands.ArgumentParsingError,
    commands.UserInputError,
    errors.BadAttachmentCount,
    errors.BadAttachmentType,
    errors.ImgurUploadError
)

IGNORE_EXCEPTIONS = (
    commands.CommandNotFound,
    commands.CheckFailure,
    commands.CheckAnyFailure
)

REPORT_ORIGINAL_EXCEPTIONS = (
    commands.CommandInvokeError,
    commands.ConversionError
)


def user_input(text: str):
    return bold(clean_content(text, max_length=32))


def str_permissions(permissions: list[str]) -> str:
    return ', '.join(perm.replace('_', ' ').title() for perm in permissions)


async def command_error(ctx: Context, error: commands.CommandError):
    if isinstance(error, commands.UserNotFound):
        await ctx.error(f'Nie znaleziono użytkownika {user_input(error.argument)}')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.error(f'Nie znaleziono członka {user_input(error.argument)}')
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.error(f'Nie znaleziono kanału {user_input(error.argument)}')
    elif isinstance(error, commands.ChannelNotReadable):
        await ctx.error(f'Nie mam uprawnień do wczytywania kanału {error.argument.mention}')
    elif isinstance(error, commands.GuildNotFound):
        await ctx.error(f'Nie znaleziono serwera {user_input(error.argument)}')
    elif isinstance(error, commands.RoleNotFound):
        await ctx.error(f'Nie znaleziono roli {user_input(error.argument)}')
    elif isinstance(error, commands.MessageNotFound):
        await ctx.error(f'Nie znaleziono wiadomości {user_input(error.argument)}')
    elif isinstance(error, (commands.EmojiNotFound, commands.PartialEmojiConversionFailure)):
        await ctx.error(f'Nie znaleziono emoji {user_input(error.argument)}')
    elif isinstance(error, commands.BadColourArgument):
        await ctx.error(f'Nieprawidłowy kolor {user_input(error.argument)}')
    elif isinstance(error, commands.BadInviteArgument):
        await ctx.error('To zaproszenie jest nieprawidłowe lub wygasło')

    elif isinstance(error, commands.BadFlagArgument):
        await ctx.error('Nieudana konwersja flagi')
    elif isinstance(error, commands.MissingFlagArgument):
        await ctx.error(f'Brakujący argument flagi {code(error.flag.name)}')
    elif isinstance(error, commands.TooManyFlags):
        await ctx.error(f'Zbyt wiele argumentów flagi {code(error.flag.name)}')
    elif isinstance(error, commands.MissingRequiredFlag):
        await ctx.error(f'Brakująca flaga {code(error.flag.name)}')

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.error(f'Argument {code(error.param.name)} jest wymagany')
    elif isinstance(error, (commands.BadArgument, commands.BadUnionArgument)):
        await ctx.error(f'Argument {code(error.param.name)} jest nieprawidłowy')
    elif isinstance(error, commands.BadLiteralArgument):
        await ctx.error(
            f"Argument {code(error.param.name)} musi mieć wartość {' | '.join(map(code, error.literals))}"
        )
    elif isinstance(error, commands.BadBoolArgument):
        await ctx.error(f'{user_input(error.argument)} jest niepoprawnym argumentem true/false')
    elif isinstance(error, commands.TooManyArguments):
        await ctx.error('Zbyt wiele argumentów')

    elif isinstance(error, commands.UnexpectedQuoteError):
        await ctx.error(f'Nieoczekiwany cudzysłów {code(error.quote)}')
    elif isinstance(error, commands.ExpectedClosingQuoteError):
        await ctx.error(f'Brak cudzysłowu zamykającego {code(error.close_quote)}')
    elif isinstance(error, commands.InvalidEndOfQuotedStringError):
        await ctx.error(f'Nieoczekiwany znak {code(error.char)} po cudzysłowie zamykającym')

    elif isinstance(error, commands.MissingPermissions):
        await ctx.error(f'Nie masz uprawnień {str_permissions(error.missing_perms)}')
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.error(f'Nie mam uprawnień {str_permissions(error.missing_perms)}')
    elif isinstance(error, commands.MissingRole):
        await ctx.error(f'Nie masz wymaganej roli {error.missing_role}')
    elif isinstance(error, commands.BotMissingRole):
        await ctx.error(f'Nie mam wymaganej roli {error.missing_role}')
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.error(f"Nie masz jednej z wymaganych ról {', '.join(error.missing_roles)}")
    elif isinstance(error, commands.BotMissingAnyRole):
        await ctx.error(f"Nie mam jednej z wymaganych ról {', '.join(error.missing_roles)}")
    elif isinstance(error, commands.NSFWChannelRequired):
        await ctx.error('Ta komenda może być użyta tylko na kanale NSFW')

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.error(f'Poczekaj jeszcze {error.retry_after:,.0f} sekund')
    elif isinstance(error, commands.MaxConcurrencyReached):
        await ctx.error(
            f'Ta komenda jest obecnie używana zbyt dużo ({error.number}/{error.per}). Spróbuj ponownie za chwilę'
        )

    elif isinstance(error, commands.DisabledCommand):
        await ctx.error('Ta komenda jest obecnie wyłączona')
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.error('Ta komenda nie może być użyta w wiadomościach prywatnych')
    elif isinstance(error, commands.PrivateMessageOnly):
        await ctx.error('Ta komenda musi być użyta w wiadomościach prywatnych')
    elif isinstance(error, commands.NotOwner):
        log.info(f'{name_id(ctx.author)} tried using {ctx.command.qualified_name} but is not the bot owner')

    elif isinstance(error, SEND_EXCEPTIONS):
        await ctx.error(clean_content(str(error), max_length=512, max_lines=4))
    elif isinstance(error, IGNORE_EXCEPTIONS):
        # TODO: remove this later
        print('IGNORED:', type(error).__name__, error)
    elif isinstance(error, REPORT_ORIGINAL_EXCEPTIONS):
        original = error.original
        if isinstance(original, discord.HTTPException):
            await ctx.error(str(original))
        elif isinstance(original, asyncio.TimeoutError):
            await ctx.error('Timeout (minął czas na połączenie z serwerem)')
        else:
            await ctx.report_exception(original)
    else:
        await ctx.report_exception(error)