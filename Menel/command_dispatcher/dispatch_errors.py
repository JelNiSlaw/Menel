from math import ceil

import discord
from cliffs import MismatchedLiteralSuggestion, MismatchedParameterType

from ..functions.clean_content import clean_content
from ..functions.plural_time import plural_time
from ..functions.stringify_permissions import stringify_permissions


def cooldown(time: float) -> str:
    return f'Poczekaj jeszcze {plural_time(ceil(time))} przed ponownym użyciem komendy.'


def missing_user_perms(perms: discord.Permissions) -> str:
    return f'Aby użyć tej komendy potrzebujesz uprawnień {stringify_permissions(perms)}.'


def missing_bot_perms(perms: discord.Permissions) -> str:
    return f'Aby wykonać tę komendę potrzebuję uprawnień {stringify_permissions(perms)}.'


def missing_global_perms(level: int) -> str:
    if level == 2:
        return 'Ta komenda wymaga uprawnień do zarządzania serwerem.'
    elif level == 3:
        return 'Ta komenda wymaga bycia administratorem serwera.'
    elif level == 4:
        return 'Ta komenda wymaga bycia właścicielem serwera.'
    elif level == 5:
        return 'Ta komenda wymaga bycia właścicielem bota.'


def mismatched_parameter_type(e: MismatchedParameterType) -> str:
    return f'Wartość `{clean_content(e.actual.value)}` nie jest ' + {
        'int': 'liczbą całkowitą',
        'float': 'liczbą',
    }.get(e.expected.typename, f'typu `{e.expected.typename}`') + '.'


def mismatched_literal_suggestion(e: MismatchedLiteralSuggestion) -> str:
    return f'Masz na myśli `{clean_content(e.expected.value)}`?\n' \
           f'Możesz napisać `tak` `yes` `t` `y`.'


def too_many_arguments():
    return 'Zbyt wiele argumentów.'


def missing_arguments():
    return 'Brakujące argumenty.'


def no_matched_variant():
    return 'Wybrano nieprawidłową opcję.'


def call_match_fail():
    return 'Niepoprawne użycie komendy.'