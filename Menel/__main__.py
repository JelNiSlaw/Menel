from os import getenv

from dotenv import load_dotenv

from . import commands, handlers
from .objects import bot
from .setup import auto_import, cliffs


load_dotenv(override=True)

auto_import(commands, cliffs, add_to_help=True)
auto_import(handlers, bot, add_to_help=False)

bot.run(getenv('DISCORD_TOKEN'), bot=True)