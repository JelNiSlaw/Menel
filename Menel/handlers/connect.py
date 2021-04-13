from .. import log
from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_connect():
        log.info(f'Connected as {bot.user.name}')
        await bot.fetch_owner()