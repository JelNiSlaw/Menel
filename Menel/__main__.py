import logging
import platform
from os import getenv

import discord
from dotenv import load_dotenv

from Menel.utils import logs
from . import PATH
from .objects.bot import Menel


def main():
    load_dotenv(PATH.parent / '.env', override=True)

    logs.setup()

    log = logging.getLogger(__name__)

    log.info(f'Python {platform.python_version()}')
    log.info(f'discord.py {discord.__version__}')

    bot = Menel()
    bot.run(getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()