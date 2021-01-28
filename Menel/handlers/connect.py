from ..objects.bot import Menel


def setup(bot: Menel):
    @bot.event
    async def on_connect():
        print(f'Connected as {bot.user.name}')
        await bot.fetch_owner()