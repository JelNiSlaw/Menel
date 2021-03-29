def main():
    from dotenv import load_dotenv

    load_dotenv(override=True)

    from os import getenv
    from .setup import auto_import, cliffs
    from .objects import bot
    from . import commands, handlers

    auto_import(commands, cliffs, add_to_help=True)
    auto_import(handlers, bot, add_to_help=False)

    bot.run(getenv('DISCORD_TOKEN'), bot=True)


if __name__ == '__main__':
    main()