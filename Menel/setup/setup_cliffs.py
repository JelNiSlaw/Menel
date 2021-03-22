import logging
from sys import stdout

import validators
from cliffs import CallMatcher, CommandDispatcher

from ..resources.regexes import DISCORD_ID


def validate_id(x: str) -> int:
    if not (match := DISCORD_ID.fullmatch(x)):
        raise ValueError()
    else:
        return int(match.group())


def validate_url(url: str) -> str:
    if not validators.url(url):
        raise ValueError()
    else:
        return url


def setup_cliffs() -> CommandDispatcher:
    logger = logging.getLogger('cliffs')
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler(stdout)
    sh.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

    logger.addHandler(sh)

    call_matcher = CallMatcher(literal_threshold=2 / 3)
    call_matcher.register_type(validate_id, 'id')
    call_matcher.register_type(validate_url, 'url')

    return CommandDispatcher(
        parser={'all_case_insensitive': True, 'simplify': 'yes'},
        matcher=call_matcher
    )


cliffs = setup_cliffs()