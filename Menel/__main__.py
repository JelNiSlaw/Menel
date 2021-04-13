from os import getenv

from . import commands, handlers, log
from .objects import bot
from .setup import auto_import, cliffs


def main():
    log.info('Starting')

    auto_import(commands, cliffs, add_to_help=True)
    auto_import(handlers, bot, add_to_help=False)

    bot.run(getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()