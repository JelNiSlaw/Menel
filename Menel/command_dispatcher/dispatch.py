from asyncio import Task
from traceback import print_exc

from cliffs import (
    CallMatchFail, MismatchedLiteral, MismatchedLiteralSuggestion, MismatchedParameterType,
    MissingLiteral, MissingParameter, MissingTail, MissingUnorderedGroup, MissingVariant, TooManyArguments,
    UnknownCommandError
)
from cliffs.syntax_tree.unordered_group import UnmatchedUnorderedGroup
from cliffs.syntax_tree.variant_group import NoMatchedVariant

from . import dispatch_errors
from .redispatch import redispatch
from ..functions import clean_content, global_perms
from ..objects import Message, cooldowns
from ..setup import cliffs


async def dispatch(command: str, m: Message, prefix: str):
    can_send_embeds = m.channel.permissions_for(m.guild.me).embed_links

    try:
        result, command = cliffs.dispatch(command, m=m, prefix=prefix)
    except MismatchedLiteralSuggestion as e:
        if can_send_embeds and not e.command.kwargs['command'].hidden:
            notice_msg = await m.error(dispatch_errors.mismatched_literal_suggestion(e))
            await redispatch(e, command, m, prefix, notice_msg)

    except MismatchedParameterType as e:
        if can_send_embeds and not e.command.kwargs['command'].hidden:
            await m.error(dispatch_errors.mismatched_parameter_type(e))

    except TooManyArguments as e:
        if can_send_embeds and not e.command.kwargs['command'].hidden:
            await m.error(dispatch_errors.too_many_arguments())

    except (
            MissingLiteral,
            MissingParameter,
            MissingTail,
            MissingUnorderedGroup,
            MissingVariant,
            UnmatchedUnorderedGroup
    ) as e:
        if can_send_embeds and not e.command.kwargs['command'].hidden:
            await m.error(dispatch_errors.missing_arguments())

    except (MismatchedLiteral, NoMatchedVariant) as e:
        if can_send_embeds and not e.command.kwargs['command'].hidden:
            await m.error(dispatch_errors.no_matched_variant())

    except CallMatchFail as e:
        if can_send_embeds and not e.command.kwargs['command'].hidden:
            await m.error(dispatch_errors.call_match_fail())

    except UnknownCommandError:
        pass

    else:
        if not result:
            return

        if not can_send_embeds:
            if not cooldowns.auto(m.author.id, '_no_embeds', 2):
                await m.send('Nie mam uprawnień do wysyłania tu embedów')
            Task(result).cancel()
            return

        command = command.kwargs['command']

        if command.global_perms and global_perms(m) < command.global_perms:
            if command.global_perms < 5 and not cooldowns.auto(m.author.id, '_global_perms', 2):
                await m.error(dispatch_errors.missing_global_perms(command.global_perms), delete_after=10)
            Task(result).cancel()
            return

        if command.user_perms and not command.user_perms < m.author.permissions_in(m.channel):
            if not cooldowns.auto(m.author.id, '_user_perms', 2):
                await m.error(dispatch_errors.missing_user_perms(command.user_perms), delete_after=10)
            Task(result).cancel()
            return

        if command.bot_perms and not command.bot_perms < m.guild.me.permissions_in(m.channel):
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
            await m.error(f'Wystąpił błąd:\n{clean_content(f"{type(e).__name__}: {e}")}')