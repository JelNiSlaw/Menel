import datetime
import logging
import pkgutil
from types import ModuleType
from typing import Union

import discord
import httpx
from discord.ext import commands

from .utils import error_handlers
from .utils.context import Context
from .utils.database import Database
from .utils.help_command import HelpCommand
from .utils.text_tools import ctx_location, name_id

log = logging.getLogger(__name__)


class Menel(commands.AutoShardedBot):
    db: Database
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
            chunk_guilds_at_startup=False,
            status=discord.Status.online,
            allowed_mentions=discord.AllowedMentions.none(),
            heartbeat_timeout=120,
        )

        self.global_rate_limit = commands.CooldownMapping.from_cooldown(5, 12, commands.BucketType.user)
        self.prefix_base = []
        self.db = Database()
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(10))

        from . import cogs

        self.load_extensions(cogs)

    async def get_prefix(self, m: Union[discord.Message, Context]) -> list[str]:
        return self.prefix_base + await self.db.get_prefixes(m.guild)

    async def process_commands(self, m: discord.Message):
        if m.author.bot:
            return

        if m.author.id in await self.db.get_blacklist():
            return

        if m.guild and not m.channel.permissions_for(m.guild.me).send_messages:
            return

        ctx = await self.get_context(m, cls=Context)

        if not ctx.command:
            return

        if self.global_rate_limit.update_rate_limit(ctx.message, ctx.command_time.timestamp()):
            log.warning(f"Rate limit exceeded by {ctx_location(ctx)}")
            return

        log.info(f"Running command {ctx.command.qualified_name} for {ctx_location(ctx)}")
        await self.invoke(ctx)

    async def on_connect(self):
        log.info(f"Connected as {name_id(self.user)}")
        self.prefix_base = [f"<@{self.user.id}>", f"<@!{self.user.id}>"]

    @staticmethod
    async def on_shard_connect(shard_id: int):
        log.debug(f"Connected on shard {shard_id}")

    @staticmethod
    async def on_ready():
        log.info("Cache ready")

    async def on_message(self, m: discord.Message):
        await self.process_commands(m)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        if not after.edited_at:
            return

        if after.edited_at - after.created_at > datetime.timedelta(minutes=2):
            return

        await self.process_commands(after)

    @staticmethod
    async def on_guild_join(guild: discord.Guild):
        log.info(f"Joined server {guild}")

    @staticmethod
    async def on_guild_remove(guild: discord.Guild):
        log.info(f"Left server {guild}")

    async def get_or_fetch_channel(
        self, id: int, /
    ) -> Union[discord.abc.GuildChannel, discord.abc.PrivateChannel, discord.Thread]:
        return self.get_channel(id) or await self.fetch_channel(id)

    async def fetch_message(self, channel_id: int, message_id: int, /) -> discord.Message:
        channel = await self.get_or_fetch_channel(channel_id)
        return await channel.fetch_message(message_id)  # type: ignore

    @staticmethod
    def find_extensions(package: ModuleType) -> set:
        def unqualify(name: str) -> str:
            return name.rsplit(".", maxsplit=1)[-1]

        exts = {"jishaku"}
        for ext in pkgutil.walk_packages(package.__path__, package.__name__ + "."):  # type: ignore
            if ext.ispkg or unqualify(ext.name).startswith("_"):
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
        log.info("Stopping the bot")
        await super().close()
        await self.client.aclose()
        self.db.client.close()
