import logging
import sys

from .. import PATH


LOGPATH = PATH.parent.joinpath('.log')


def setup() -> None:
    log = logging.getLogger()
    discord_log = logging.getLogger('discord')

    log.setLevel(logging.DEBUG)
    discord_log.setLevel(logging.WARNING)

    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(filename=LOGPATH, mode='w', encoding='utf-8')

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s:%(module)s] %(message)s'))

    discord_log.propagate = False

    log.addHandler(console_handler)
    log.addHandler(file_handler)
    discord_log.addHandler(console_handler)
    discord_log.addHandler(file_handler)