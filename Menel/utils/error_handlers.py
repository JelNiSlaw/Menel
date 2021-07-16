import math

import discord
import httpx
from discord.ext import commands
from discord.ext.commands import BucketType

from . import embeds, errors
from .context import Context
from .markdown import code
from .misc import clamp
from .text_tools import escape, limit_length, plural_time, str_permissions, user_input


async def command_error(ctx: Context, error: commands.CommandError) -> None:
    # sourcery no-metrics
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.UserInputError):
        if isinstance(error, commands.TooManyArguments):
            await ctx.error('Zbyt wiele argumentów')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.error(f'Argument {code(error.param.name)} jest wymagany')

        if isinstance(error, commands.BadArgument):
            if isinstance(error, commands.UserNotFound):
                await ctx.error(f'Nie znaleziono użytkownika {user_input(error.argument)}')
            elif isinstance(error, commands.MemberNotFound):
                await ctx.error(f'Nie znaleziono członka {user_input(error.argument)}')
            elif isinstance(error, commands.ChannelNotFound):
                await ctx.error(f'Nie znaleziono kanału {user_input(str(error.argument))}')
            elif isinstance(error, commands.ChannelNotReadable):
                await ctx.error(f'Nie mam uprawnień do czytania kanału {error.argument.mention}')
            elif isinstance(error, commands.MessageNotFound):
                await ctx.error(f'Nie znaleziono wiadomości {user_input(error.argument)}')
            elif isinstance(error, commands.RoleNotFound):
                await ctx.error(f'Nie znaleziono roli {user_input(error.argument)}')
            elif isinstance(error, commands.GuildNotFound):
                await ctx.error(f'Nie znaleziono serwera {user_input(error.argument)}')
            elif isinstance(error, commands.BadInviteArgument):
                await ctx.error(f'Zaproszenie {user_input(error.argument)} jest nieprawidłowe lub wygasło')
            elif isinstance(error, (commands.EmojiNotFound, commands.PartialEmojiConversionFailure)):
                await ctx.error(f'Nie znaleziono niestandardowego emoji {user_input(error.argument)}')
            elif isinstance(error, commands.ObjectNotFound):
                await ctx.error(f'{user_input(error.argument)} nie jest prawidłowym ID')
            elif isinstance(error, commands.BadBoolArgument):
                await ctx.error(f'{user_input(error.argument)} jest niepoprawnym argumentem true/false')
            elif isinstance(error, commands.BadColorArgument):
                await ctx.error(f'Nieprawidłowy kolor {user_input(error.argument)}')

            elif isinstance(error, commands.FlagError):
                if isinstance(error, commands.MissingFlagArgument):
                    await ctx.error(f'Brakujący argument flagi {code(error.flag.name)}')
                elif isinstance(error, commands.TooManyFlags):
                    await ctx.error(f'Zbyt wiele argumentów flagi {code(error.flag.name)}')
                elif isinstance(error, commands.MissingRequiredFlag):
                    await ctx.error(f'Brakująca flaga {code(error.flag.name)}')
                else:
                    await ctx.error('Nieudana konwersja flagi')

            elif isinstance(error, errors.BadNumber):
                await ctx.error(f'{error.name} nie może być {error.problem} niż {error.value}')
            elif isinstance(error, errors.BadLanguage):
                await ctx.error(f'Podano nieprawiłowy język {user_input(error.argument)}')
            else:
                await ctx.error(f'Nie udało się przekonwertować argumentu ({escape(str(error))})')

        elif isinstance(error, commands.BadUnionArgument):
            await ctx.error(f'Argument {code(error.param.name)} jest nieprawidłowy')
        elif isinstance(error, commands.BadLiteralArgument):
            await ctx.error(
                f"Argument {code(error.param.name)} musi mieć wartość {' | '.join(map(code, error.literals))}"
            )

        elif isinstance(error, commands.ArgumentParsingError):
            if isinstance(error, commands.UnexpectedQuoteError):
                await ctx.error(f'Nieoczekiwany cudzysłów {code(error.quote)}')
            elif isinstance(error, commands.ExpectedClosingQuoteError):
                await ctx.error(f'Brak cudzysłowu zamykającego {code(error.close_quote)}')
            elif isinstance(error, commands.InvalidEndOfQuotedStringError):
                await ctx.error(f'Nieoczekiwany znak {code(error.char)} po cudzysłowie zamykającym')

    elif isinstance(error, commands.CheckFailure):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=embeds.with_author(
                    ctx.author,
                    description=f'Nie posiadasz uprawnień: {str_permissions(error.missing_permissions)}',
                    color=discord.Color.red()
                ).set_footer(text=f'{ctx.author.name} is not in the sudoers file. This incident will be reported.')
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.error(f'Nie posiadam uprawnień: {str_permissions(error.missing_permissions)}')
        elif isinstance(error, commands.NotOwner):
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.error('Ta komenda nie może być użyta w wiadomościach prywatnych')
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.error('Ta komenda musi być użyta w wiadomościach prywatnych')
        elif isinstance(error, commands.NSFWChannelRequired):
            await ctx.error('Ta komenda może być użyta tylko na kanale NSFW')
        elif isinstance(error, commands.CheckAnyFailure):
            await ctx.error('Nie spełniasz wymagań do użycia tej komendy')
        elif isinstance(error, commands.MissingRole):
            await ctx.error(f'Nie masz wymaganej roli {error.missing_role}')
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.error(f"Nie masz jednej z wymaganych ról {', '.join(error.missing_roles)}")
        elif isinstance(error, commands.BotMissingRole):
            await ctx.error(f'Nie mam wymaganej roli {error.missing_role}')
        elif isinstance(error, commands.BotMissingAnyRole):
            await ctx.error(f"Nie mam jednej z wymaganych ról {', '.join(error.missing_roles)}")

        elif isinstance(error, errors.BadAttachmentCount):
            await ctx.error(str(error))
        elif isinstance(error, errors.BadAttachmentType):
            await ctx.error(f'Nieprawidłowy typ załącznika {code(error.type)}')

    elif isinstance(error, commands.DisabledCommand):
        await ctx.error('Ta komenda jest obecnie wyłączona')
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.error(
            f'Poczekaj jeszcze {plural_time(math.ceil(error.retry_after))}',
            delete_after=clamp(error.retry_after, 2, 30)
        )
    elif isinstance(error, commands.MaxConcurrencyReached):
        per = {
            BucketType.default: 'globalnie',
            BucketType.user: 'użytkownika',
            BucketType.member: 'członka serwera',
            BucketType.guild: 'serwer',
            BucketType.channel: 'kanał',
            BucketType.category: 'kategorię',
            BucketType.role: 'rolę'
        }[error.per]
        await ctx.error(f'Ta komenda jest obecnie używana zbyt dużo ({error.number}/{per}). Spróbuj ponownie za chwilę')

    elif isinstance(error, (commands.CommandInvokeError, commands.ConversionError)):
        original = error.original
        if isinstance(original, discord.HTTPException):
            await ctx.error(str(original))
        elif isinstance(original, httpx.TimeoutException):
            await ctx.error('Timeout (minął czas na połączenie z serwerem)')

        elif isinstance(original, errors.ImgurUploadError):
            message = escape(limit_length(original.message, max_length=1024, max_lines=4))
            await ctx.error(f'{original.code}: {message}')
        else:
            await ctx.report_exception(original)