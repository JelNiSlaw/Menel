from os import getenv

from dotenv import load_dotenv


load_dotenv(override=True)


def main():
    from . import commands, handlers
    from .objects import bot
    from .setup import auto_import, cliffs

    auto_import(commands, cliffs, add_to_help=True)
    auto_import(handlers, bot, add_to_help=False)

    bot.run(getenv('DISCORD_TOKEN'), bot=True)


if __name__ == '__main__':
    main()