import discord
from discord.ext import commands, tasks

from Menel.utils.text_tools import plural

from ..bot import Menel


class Tasks(commands.Cog):
    def __init__(self, bot: Menel):
        self.bot = bot

        self._last_status_data = None
        self._message_count = 0
        self._db_message_count = 0

        self.status_loop.start()
        self.message_count_loop.start()

    @tasks.loop(seconds=20)
    async def status_loop(self):
        users = sum(g.member_count for g in self.bot.guilds)
        guilds = len(self.bot.guilds)
        message_count = self._message_count + self._db_message_count
        latency = self.bot.latency

        status_data = users, guilds, message_count, latency

        if status_data == self._last_status_data:
            return

        users = plural(users, "użytkownik", "użytkowników", "użytkowników")
        guilds = plural(guilds, "serwer", "serwery", "serwerów")
        message_count = plural(message_count, "wiadomość", "wiadomości", "wiadomości")
        latency = f"{latency * 1000:,.0f} ms"

        self._last_status_data = status_data
        await self.bot.change_presence(
            activity=discord.Activity(
                name=" | ".join((users, guilds, message_count, latency)), type=discord.ActivityType.watching
            )
        )

    @tasks.loop(minutes=5)
    async def message_count_loop(self):
        if self._message_count > 0:
            self._db_message_count = await self.bot.db.increase_message_count(self._message_count)
            self._message_count = 0

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()

    @message_count_loop.before_loop
    async def before_message_count_loop(self):
        await self.bot.wait_until_ready()
        self._db_message_count = await self.bot.db.get_message_count()

    @message_count_loop.after_loop
    async def after_message_count_loop(self):
        if self._message_count > 0:
            await self.bot.db.increase_message_count(self._message_count)

    @commands.Cog.listener()
    async def on_message(self, _):
        self._message_count += 1


def setup(bot: Menel):
    bot.add_cog(Tasks(bot))
