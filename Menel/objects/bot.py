import logging
import pkgutil
from datetime import timedelta
from types import ModuleType
from typing import Union

import discord
import httpx
from discord.ext import commands, tasks

from .database import Database
from .help_command import HelpCommand
from ..objects.context import Context
from ..utils import error_handlers
from ..utils.text_tools import ctx_location, name_id, plural


log = logging.getLogger(__name__)


class Menel(commands.AutoShardedBot):
    on_command_error = staticmethod(error_handlers.command_error)

    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            case_insensitive=True,
            owner_id=724674729977577643,
            help_command=HelpCommand(),
            strip_after_prefix=True,
            max_messages=5 * 1024,
            intents=discord.Intents(messages=True, guilds=True, members=True, reactions=True),
            member_cache_flags=discord.MemberCacheFlags(joined=True, voice=False),
            chunk_guilds_at_startup=True,
            status=discord.Status.online,
            allowed_mentions=discord.AllowedMentions.none(),
            heartbeat_timeout=120
        )

        self.prefix_base = []
        self.global_rate_limit = commands.CooldownMapping.from_cooldown(5, 15, commands.BucketType.user)
        self.db = Database()
        self.client = httpx.AsyncClient()

        from .. import cogs
        self.load_extensions(cogs)

        self._last_status_data = None
        self.status_loop.start()

    async def get_prefix(self, m: Union[discord.Message, Context]) -> list[str]:
        return self.prefix_base + await self.db.get_prefixes(m.guild)

    async def process_commands(self, m: discord.Message):
        if m.author.bot:
            return

        if m.guild and not m.channel.permissions_for(m.guild.me).send_messages:
            return

        ctx = await self.get_context(m, cls=Context)

        if not ctx.command:
            return

        if self.global_rate_limit.update_rate_limit(ctx.message, ctx.command_time.timestamp()):
            log.warning(f'Rate limit exceeded by {ctx_location(ctx)}')
            return

        log.info(f'Running command {ctx.command.qualified_name} for {ctx_location(ctx)}')
        await self.invoke(ctx)

    async def on_connect(self):
        log.info(f'Connected as {name_id(self.user)}')
        self.prefix_base = [f'<@{self.user.id}>', f'<@!{self.user.id}>']

    @staticmethod
    async def on_shard_connect(shard_id: int):
        log.debug(f'Connected on shard {shard_id}')

    @staticmethod
    async def on_ready():
        log.info('Cache ready')

    async def on_message(self, m: discord.Message):
        await self.process_commands(m)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        if not after.edited_at:
            return

        if after.edited_at - after.created_at > timedelta(minutes=2):
            return

        await self.process_commands(after)

    @staticmethod
    async def on_guild_join(guild: discord.Guild):
        log.info(f'Joined server {guild}')

    @staticmethod
    async def on_guild_remove(guild: discord.Guild):
        log.info(f'Left server {guild}')

    @staticmethod
    def find_extensions(package: ModuleType) -> set:
        def unqualify(name: str) -> str:
            return name.rsplit('.', maxsplit=1)[-1]

        exts = {'jishaku'}
        for ext in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            if ext.ispkg or unqualify(ext.name).startswith('_'):
                continue
            exts.add(ext.name)
        return exts

    def load_extensions(self, package: ModuleType):
        for ext in self.find_extensions(package):
            self.load_extension(ext)

    def reload_extensions(self):
        for ext in self.extensions.copy():
            self.reload_extension(ext)

    async def close(self):
        log.info('Stopping the bot')
        await super().close()
        await self.client.aclose()
        self.db.client.close()

    @tasks.loop(seconds=20)
    async def status_loop(self):
        users = sum(g.member_count for g in self.guilds)
        guilds = len(self.guilds)
        latency = self.latency

        status_data = users, guilds, latency

        if status_data != self._last_status_data:
            self._last_status_data = status_data
            await self.change_presence(
                activity=discord.Activity(
                    name=f"{plural(users, 'użytkownik', 'użytkowników', 'użytkowników')} | "
                         f"{plural(guilds, 'serwer', 'serwery', 'serwerów')} | "
                         f"{latency * 1000:,.0f} ms",
                    type=discord.ActivityType.watching
                )
            )

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.wait_until_ready()