from asyncio import Task
from traceback import print_exc

from cliffs import (
    CallMatchFail, MismatchedLiteral, MismatchedLiteralSuggestion, MismatchedParameterType,
    MissingLiteral, MissingParameter, MissingTail, MissingUnorderedGroup, MissingVariant, TooManyArguments,
    UnknownCommandError
)
from cliffs.syntax_tree.unordered_group import UnmatchedUnorderedGroup
from cliffs.syntax_tree.variant_group import NoMatchedVariant

from ..command_dispatcher import dispatch_errors
from ..command_dispatcher.redispatch import redispatch
from ..functions.clean_content import clean_content
from ..functions.user_perms import user_perms
from ..objects.cooldowns import cooldowns
from ..objects.message import Message
from ..setup.setup_cliffs import cliffs


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

        if 'perms' in command.kwargs and user_perms(m) < command.kwargs['perms']:
            await m.error(dispatch_errors.missing_perms(command.kwargs['perms']), delete_after=5)
            Task(result).cancel()
            return

        if not (cooldown := cooldowns.auto(m.author.id, command.kwargs['name'], command.kwargs['cooldown'])):
            try:
                await result
            except Exception as e:
                print_exc()
                await m.error(f'An error occurred\n{clean_content(e)}')
        else:
            Task(result).cancel()
            if not cooldowns.auto(m.author.id, '_cooldown', 2):
                await m.error(dispatch_errors.cooldown(cooldown), delete_after=5)