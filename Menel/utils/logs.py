import logging
import sys

from Menel import PATH


LOGPATH = PATH.parent.joinpath('.log')


def setup() -> None:
    log = logging.getLogger()
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('pyppeteer').setLevel(logging.INFO)

    log.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(filename=LOGPATH, mode='w', encoding='utf-8')

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s:%(module)s] %(message)s'))

    log.addHandler(console_handler)
    log.addHandler(file_handler)