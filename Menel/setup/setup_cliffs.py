import logging
from sys import stdout

from cliffs import CallMatcher, CommandDispatcher


def setup_cliffs() -> CommandDispatcher:
    logger = logging.getLogger('cliffs')
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler(stdout)
    sh.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

    logger.addHandler(sh)

    return CommandDispatcher(
        parser={'all_case_insensitive': True, 'simplify': 'yes'},
        matcher=CallMatcher(literal_threshold=0.5)
    )


cliffs = setup_cliffs()