from asyncio import Task
from traceback import print_exc

from cliffs import (
    CallMatchFail, MismatchedLiteral, MismatchedLiteralSuggestion, MismatchedParameterType,
    MissingLiteral, MissingParameter, MissingTail, MissingUnorderedGroup, MissingVariant, TooManyArguments,
    UnknownCommandError
)
from cliffs.syntax_tree.unordered_group import UnmatchedUnorderedGroup
from cliffs.syntax_tree.variant_group import NoMatchedVariant

from ..command_dispatcher import dispatch_errors, redispatch
from ..functions import clean_content, global_perms
from ..objects import cooldowns, Message
from ..setup import cliffs


async def dispatch(command: str, m: Message, prefix: str):
    try:
        result, command = cliffs.dispatch(command, m=m, prefix=prefix)
    except MismatchedLiteralSuggestion as e:
        notice_msg = await m.error(dispatch_errors.mismatched_literal_suggestion(e))
        await redispatch(e, m, prefix, notice_msg)

    except MismatchedParameterType as e:
        await m.error(dispatch_errors.mismatched_parameter_type(e))

    except TooManyArguments:
        await m.error(dispatch_errors.too_many_arguments())

    except (MissingLiteral,
            MissingParameter,
            MissingTail,
            MissingUnorderedGroup,
            MissingVariant,
            UnmatchedUnorderedGroup):
        await m.error(dispatch_errors.missing_arguments())

    except (MismatchedLiteral, NoMatchedVariant):
        await m.error(dispatch_errors.no_matched_variant())

    except CallMatchFail:
        await m.error(dispatch_errors.call_match_fail())

    except UnknownCommandError:
        pass

    else:
        if not result:
            return

        if not m.guild.me.permissions_in(m.channel).send_messages:
            return

        command = command.kwargs['command']

        if global_perms(m) < command.global_perms:
            if not cooldowns.auto(m.author.id, '_global_perms', 2):
                await m.error(dispatch_errors.missing_global_perms(command.global_perms), delete_after=10)
            Task(result).cancel()
            return

        if not command.user_perms < m.author.permissions_in(m.channel):
            if not cooldowns.auto(m.author.id, '_user_perms', 2):
                await m.error(dispatch_errors.missing_user_perms(command.user_perms), delete_after=10)
            Task(result).cancel()
            return

        if not command.bot_perms < m.guild.me.permissions_in(m.channel):
            if not cooldowns.auto(m.author.id, '_bot_perms', 2):
                await m.error(dispatch_errors.missing_bot_perms(command.bot_perms), delete_after=10)
            Task(result).cancel()
            return

        if command.cooldown:
            if cooldown := cooldowns.auto(m.author.id, command.name, command.cooldown):
                if not cooldowns.auto(m.author.id, '_cooldown', 2):
                    await m.error(dispatch_errors.cooldown(cooldown), delete_after=10)
                Task(result).cancel()
                return

        try:
            await result
        except Exception as e:
            print_exc()
            await m.error(f'An error occurred\n{clean_content(f"{type(e).__name__}: {e}")}')