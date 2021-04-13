from .. import log
from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_ready():
        log.info('Bot ready')