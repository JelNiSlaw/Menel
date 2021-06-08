from os import getenv
from typing import Optional

import discord
import motor.motor_asyncio


DEFAULT_PREFIXES = ['?']


class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            getenv('MONGODB_CONNECTION_STRING'),
            tz_aware=False,
            connect=True,
            directConnection=False,
            appname='Menel',
            retryWrites=True,
            retryReads=True,
            compressors='zlib',
            zlibCompressionLevel=5,
            w=1,
            readPreference='primaryPreferred',
            tls=True
        )

        self._prefix_cache = {}

        self._db = self.client['bot']
        self.config = self._db['config']

    async def get_prefixes(self, guild: Optional[discord.Guild]) -> list[str]:
        if guild is None:
            return DEFAULT_PREFIXES

        if guild.id not in self._prefix_cache:
            document = await self.config.find_one(guild.id)
            if not document or 'prefixes' not in document:
                self._prefix_cache[guild.id] = []
            else:
                self._prefix_cache[guild.id] = document['prefixes']

        return self._prefix_cache[guild.id] or DEFAULT_PREFIXES

    async def set_prefixes(self, guild: discord.Guild, prefixes: list[str]) -> None:
        await self.config.update_one({'_id': guild.id}, {'$set': {'prefixes': prefixes}}, upsert=True)
        self._prefix_cache[guild.id] = prefixes

    async def reset_prefixes(self, guild: discord.Guild) -> None:
        await self.config.update_one({'_id': guild.id}, {'$unset': {'prefixes': None}}, upsert=True)
        self._prefix_cache[guild.id] = []