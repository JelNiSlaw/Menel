import logging
import platform
from os import environ

import discord
from discord.http import Route
from dotenv import load_dotenv

from . import PATH
from .bot import Menel
from .utils import logs


def main():
    load_dotenv(PATH.parent / ".env", override=True)
    logs.setup()
    log = logging.getLogger(__name__)

    Route.BASE = Route.BASE.replace("//discord.com/", "//canary.discord.com/")

    log.info(f"Python {platform.python_version()}")
    log.info(f"discord.py {discord.__version__}")

    bot = Menel()
    bot.run(environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    main()
