import asyncio
import logging
import pkgutil
import sys
import traceback
from datetime import timedelta
from types import ModuleType

import discord
from discord.ext import commands, tasks

from ..objects.context import Context
from ..utils import errors
from ..utils.text_tools import ctx_location, name_id, plural


log = logging.getLogger(__name__)


class Menel(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(','),
            case_insensitive=True,
            owner_id=724674729977577643,
            description='Cześć!',
            strip_after_prefix=True,
            max_messages=5 * 1024,
            intents=discord.Intents(
                guilds=True,
                members=True,
                bans=False,
                emojis=False,
                integrations=False,
                webhooks=False,
                invites=False,
                voice_states=False,
                presences=False,
                messages=True,
                reactions=True,
                typing=False
            ),
            member_cache_flags=discord.MemberCacheFlags(voice=False, joined=True),
            chunk_guilds_at_startup=True,
            status=discord.Status.online,
            allowed_mentions=discord.AllowedMentions.none(),
            heartbeat_timeout=120
        )

        from .. import cogs
        self.load_extensions(cogs)

        self.owners = []
        self.cooldowns = {}
        self._last_status_data = None
        self.status_loop.start()

    @staticmethod
    def get_extensions(package: ModuleType) -> set:

        def unqualify(name: str) -> str:
            return name.rsplit('.', maxsplit=1)[-1]

        exts = set()

        for ext in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            if ext.ispkg or unqualify(ext.name).startswith('_'):
                continue

            exts.add(ext.name)
        exts.add('jishaku')
        return exts

    def load_extensions(self, package: ModuleType):
        for ext in self.get_extensions(package):
            self.load_extension(ext)

    def reload_extensions(self):
        for ext in self.extensions.copy():
            self.reload_extension(ext)

    async def process_commands(self, m: discord.Message):
        if m.author.bot or not m.channel.permissions_for(m.guild.me).send_messages:
            return

        ctx = await self.get_context(m, cls=Context)
        if ctx.command:
            log.info(f'Running command {ctx.command.name} for {ctx_location(ctx)}')
        await self.invoke(ctx)

    async def on_connect(self):
        log.info(f'Connected as {name_id(self.user)}')

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

        if after.edited_at - after.created_at > timedelta(minutes=1):
            return

        await self.process_commands(after)

    @staticmethod
    async def on_guild_join(guild: discord.Guild):
        log.info(f'Joined server {guild}')

    @staticmethod
    async def on_guild_remove(guild: discord.Guild):
        log.info(f'Left server {guild}')

    async def on_command_error(self, ctx: Context, error: Exception):
        ignored_exceptions = (
            commands.CommandNotFound,
            commands.CheckFailure
        )  # , commands.CommandError)
        send_exceptions = (
            commands.CommandInvokeError,
                # commands.BadArgument,
            commands.ArgumentParsingError,
            errors.BadAttachmentCount,
            errors.BadAttachmentType,
            errors.ImgurUploadError
        )

        try:
            raise error
        except send_exceptions:
            await ctx.error(str(error))
        except commands.NoPrivateMessage:
            await ctx.error('Ta komenda nie może być użyta w wiadomościach prywatnych')
        except commands.DisabledCommand:
            await ctx.author.send('Ta komenda jest obecnie wyłączona')
        except commands.NotOwner:
            log.info(f'{name_id(ctx.author)} tried using {ctx.command.name} but is not the bot owner')
        except asyncio.TimeoutError:
            await ctx.error('Minął czas na połączenie z serwerem')
        except ignored_exceptions:
            print('IGNORED:', type(error).__name__, error)
        except Exception:
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await ctx.report_exception(error)

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
                         f"{round(latency * 1000):,} ms",
                    type=discord.ActivityType.watching
                )
            )

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.wait_until_ready()