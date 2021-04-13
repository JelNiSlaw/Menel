from .. import log
from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_shard_connect(shard_id: int):
        log.debug(f'Connected on shard {shard_id}')