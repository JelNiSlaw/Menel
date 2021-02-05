from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_ready():
        print('Bot ready')