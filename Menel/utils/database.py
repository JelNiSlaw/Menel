from os import environ
from typing import Any, Hashable, Optional

import discord
import motor
import motor.motor_asyncio
import pymongo


class DocumentCache:
    def __init__(self, collection: pymongo.collection.Collection, default: Any = None):
        self.collection = collection
        self.default = default
        self.cache = {}

    async def get(self, document_id: Hashable, key: Optional[str]) -> Optional[Any]:
        if document_id is None or key is None:
            return self.default[key]

        cache = self.cache.get(document_id)
        if cache is None:
            document = await self.collection.find_one(document_id)
            if document is None:
                self.cache[document_id] = {}
            else:
                del document['_id']
                self.cache[document_id] = document
                if key in document:
                    return document[key]

        elif key in cache:
            return cache[key]
        return self.default[key]

    async def set(self, document_id: Hashable, key: str, value: Any) -> None:
        await self.collection.update_one({'_id': document_id}, {'$set': {key: value}}, upsert=True)
        self.prepare_document(document_id)
        self.cache[document_id][key] = value

    async def add_to_set(self, document_id: Hashable, key: str, *values: Any):
        await self.collection.update_one({'_id': document_id}, {'$addToSet': {key: {'$each': values}}}, upsert=True)
        self.prepare_list(document_id, key)
        self.cache[document_id][key].extend(values)
        self.cache[document_id][key] = list(set(self.cache[document_id][key]))

    async def pull(self, document_id: Hashable, key: str, *values: Any):
        await self.collection.update_one({'_id': document_id}, {'$pull': {key: {'$in': values}}}, upsert=True)
        self.prepare_list(document_id, key)
        cache = set(self.cache[document_id][key])
        cache.difference_update(values)
        self.cache[document_id][key] = list(cache)

    async def unset(self, document_id: Hashable, key: str) -> None:
        await self.collection.update_one({'_id': document_id}, {'$unset': {key: None}}, upsert=True)
        try:
            del self.cache[document_id][key]
        except KeyError:
            pass

    def prepare_document(self, document_id: Hashable) -> None:
        if document_id not in self.cache:
            self.cache[document_id] = {}

    def prepare_list(self, document_id: Hashable, key: str) -> None:
        self.prepare_document(document_id)
        if key not in self.cache[document_id]:
            self.cache[document_id][key] = []


class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            host=environ['DB_HOST'],
            tz_aware=False,
            connect=True,
            directConnection=False,
            appname='Menel',
            retryWrites=True,
            retryReads=True,
            compressors='zlib',
            zlibCompressionLevel=5,
            w=1,
            readPreference='primaryPreferred'
        )

        self._db = self.client['bot']
        self.name_history = self._db['name_history']
        self.bot_config = self._db['bot_config']
        self.guild_config = self._db['guild_config']
        self.bot_config_cache = DocumentCache(self.bot_config, {'users': []})
        self.guild_config_cache = DocumentCache(self.guild_config, {'prefixes': ['?']})

    # prefixes

    async def get_prefixes(self, guild: Optional[discord.Guild]) -> list[str]:
        return await self.guild_config_cache.get(guild.id if guild else None, 'prefixes')

    async def set_prefixes(self, guild_id: int, prefixes: list[str]) -> None:
        await self.guild_config_cache.set(guild_id, 'prefixes', prefixes)

    async def reset_prefixes(self, guild_id: int) -> None:
        await self.guild_config_cache.unset(guild_id, 'prefixes')

    # blacklist

    async def get_blacklist(self) -> set[int]:
        return set(await self.bot_config_cache.get('blacklist', 'users'))

    async def add_blacklist(self, *user_ids: int) -> None:
        await self.bot_config_cache.add_to_set('blacklist', 'users', *user_ids)

    async def remove_blacklist(self, *user_ids: int) -> None:
        await self.bot_config_cache.pull('blacklist', 'users', *user_ids)

    # message count

    async def get_message_count(self) -> int:
        document = await self.bot_config.find_one('stats')
        return document['message_count']

    async def increase_message_count(self, amount: int) -> int:
        document = await self.bot_config.find_one_and_update({'_id': 'stats'}, {'$inc': {'message_count': amount}},
            projection={'message_count': True, '_id': False}, upsert=True, return_document=pymongo.ReturnDocument.AFTER)
        return document['message_count']

    # name history

    async def get_name_history(self, user_id: int) -> list[str]:
        document = await self.name_history.find_one(user_id)
        return document['names'] if document else []

    async def add_name_history(self, user_id: int, name: str) -> None:
        await self.name_history.update_one({'_id': user_id}, {'$push': {'names': name}}, upsert=True)