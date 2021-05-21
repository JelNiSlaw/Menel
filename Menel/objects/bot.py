import discord
from discord import AutoShardedClient
from discord.ext import tasks

from ..resources.statuses import random_status


class Menel(AutoShardedClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.owners = []
        self.cooldowns = {}

        self.status_loop.start()


    async def fetch_owner(self) -> discord.User:
        app = await self.application_info()
        self.owners = app.team.members if app.team else [app.owner]
        return self.owners


    def is_owner(self, user_id: int) -> bool:
        return user_id in (o.id for o in self.owners)


    @tasks.loop(seconds=30)
    async def status_loop(self):
        await self.change_presence(
            activity=discord.Activity(
                name=random_status(self),
                type=discord.ActivityType.watching
            )
        )


    @status_loop.before_loop
    async def before_status_loop(self):
        await self.wait_until_ready()


bot = Menel(
    max_messages=10000,
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