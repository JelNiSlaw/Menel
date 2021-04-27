import logging
import platform
from os import getenv

import discord
from dotenv import load_dotenv

from . import PATH, commands, handlers
from .objects import bot
from .setup import auto_import, cliffs, logs


def main():
    load_dotenv(PATH.parent / '.env', override=True)

    logs.setup()

    log = logging.getLogger(__name__)

    log.info(f'Python {platform.python_version()}')
    log.info(f'discord.py {discord.__version__}')

    auto_import(commands, cliffs, add_to_help=True)
    auto_import(handlers, bot, add_to_help=False)

    bot.run(getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()