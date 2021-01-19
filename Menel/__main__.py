import os

from . import commands, handlers
from .objects.bot import bot
from .setup.auto_import import auto_import
from .setup.setup_cliffs import cliffs


auto_import(commands, cliffs)
auto_import(handlers, bot)

bot.run(os.getenv('DISCORD_TOKEN'), bot=True)