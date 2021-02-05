import os

from . import commands, handlers
from .objects import bot
from .setup.auto_import import auto_import
from .setup.setup_cliffs import cliffs


auto_import(commands, cliffs, add_to_help=True)
auto_import(handlers, bot, add_to_help=False)

bot.run(os.getenv('DISCORD_TOKEN'), bot=True)