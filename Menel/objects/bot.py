import discord
from discord import AutoShardedClient


class Menel(AutoShardedClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.owner = None

        self.cooldowns = {}


    async def fetch_owner(self) -> discord.User:
        app = await self.application_info()
        self.owner = app.team.owner if app.team else app.owner
        return self.owner


# noinspection PyTypeChecker
# bad detected type
bot = Menel(
    max_messages=10000,
    intents=discord.Intents(
        guilds=True,
        members=True,
        bans=True,
        emojis=False,
        integrations=False,
        webhooks=False,
        invites=False,
        voice_states=False,
        presences=True,
        messages=True,
        reactions=True,
        typing=False
    ),
    member_cache_flags=discord.MemberCacheFlags(online=True, voice=False, joined=True),
    chunk_guilds_at_startup=True,
    status=discord.Status.online,
    activity=discord.Activity(name='Menel Rewrite', type=discord.ActivityType.watching),
    allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False),
    heartbeat_timeout=10,
    guild_ready_timeout=5,
    guild_subscriptions=True
)