import logging

from ..objects import Menel


log = logging.getLogger(__name__)


def setup(bot: Menel):
    @bot.event
    async def on_connect():
        log.info(f'Connected as {bot.user.name}')
        await bot.fetch_owner()