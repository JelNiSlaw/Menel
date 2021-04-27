import discord
from discord import AutoShardedClient


class Menel(AutoShardedClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.owners = None

        self.cooldowns = {}


    async def fetch_owner(self) -> discord.User:
        app = await self.application_info()
        self.owners = app.team.members if app.team else [app.owner]
        return self.owners


    def is_owner(self, user_id: int) -> bool:
        return user_id in (o.id for o in self.owners)


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
    activity=discord.Activity(name='Menel Rewrite', type=discord.ActivityType.watching),
    allowed_mentions=discord.AllowedMentions.none(),
    heartbeat_timeout=120
)