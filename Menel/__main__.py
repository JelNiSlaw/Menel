import logging
from os import getenv

from . import commands, handlers
from .objects import bot
from .setup import auto_import, cliffs, logs


log = logging.getLogger(__name__)


def main():
    logs.setup()

    log.info('Starting')

    auto_import(commands, cliffs, add_to_help=True)
    auto_import(handlers, bot, add_to_help=False)

    bot.run(getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()