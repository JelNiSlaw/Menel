from collections import defaultdict
from os import environ
from typing import Any, Hashable, Optional

import discord
import motor
import motor.motor_asyncio
import pymongo
import pymongo.collection


class CollectionCache:
    _update_kwargs = {"projection": {"_id": False}, "upsert": True, "return_document": pymongo.ReturnDocument.AFTER}

    def __init__(self, collection: Any) -> None:
        self.collection = collection
        self.cache: defaultdict[Hashable, Optional[dict]] = defaultdict(dict)

    async def get(self, document_id: Hashable, key: str) -> Optional[Any]:
        if document_id not in self.cache:
            print(document_id, key)
            document = await self.collection.find_one(document_id)
            if document is not None:
                id = document.pop("_id")
                self.cache[id] = document
                return document.get(key)
            else:
                self.cache[document_id] = None
                return None

        cache = self.cache[document_id]
        if cache is not None:
            return cache.get(key)
        else:
            return None

    async def set(self, document_id: Hashable, key: str, value: Any) -> None:
        self.cache[document_id] = await self.collection.find_one_and_update(
            {"_id": document_id}, {"$set": {key: value}}, **self._update_kwargs
        )

    async def unset(self, document_id: Hashable, key: str) -> None:
        self.cache[document_id] = await self.collection.find_one_and_update(
            {"_id": document_id}, {"$unset": {key: None}}, **self._update_kwargs
        )

    async def add_to_set(self, document_id: Hashable, key: str, *values: Any) -> None:
        self.cache[document_id] = await self.collection.find_one_and_update(
            {"_id": document_id}, {"$addToSet": {key: {"$each": values}}}, **self._update_kwargs
        )

    async def pull(self, document_id: Hashable, key: str, *values: Any) -> None:
        self.cache[document_id] = await self.collection.find_one_and_update(
            {"_id": document_id}, {"$pull": {key: {"$in": values}}}, **self._update_kwargs
        )


class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            host=environ["DB_HOST"],
            tz_aware=False,
            connect=True,
            directConnection=False,
            appname="Menel",
            retryWrites=True,
            retryReads=True,
            compressors="zlib",
            zlibCompressionLevel=5,
            w=1,
            readPreference="primaryPreferred",
        )

        self._db = self.client["bot"]
        self.name_history = self._db["name_history"]
        self.bot_config = self._db["bot_config"]
        self.guild_config = self._db["guild_config"]

        self.bot_config_cache = CollectionCache(self.bot_config)
        self.guild_config_cache = CollectionCache(self.guild_config)

    # prefixes

    async def get_prefixes(self, guild: Optional[discord.Guild]) -> list[str]:
        default = [".", "?"]
        if guild is None:
            return default
        prefixes = await self.guild_config_cache.get(guild.id, "prefixes")
        if prefixes is not None:
            return prefixes
        return default

    async def set_prefixes(self, guild_id: int, prefixes: list[str]) -> None:
        await self.guild_config_cache.set(guild_id, "prefixes", prefixes)

    async def reset_prefixes(self, guild_id: int) -> None:
        await self.guild_config_cache.unset(guild_id, "prefixes")

    # blacklist

    async def get_blacklist(self) -> list[int]:
        users = await self.bot_config_cache.get("blacklist", "users")
        if users is not None:
            return users
        return []

    async def add_blacklist(self, *user_ids: int) -> None:
        await self.bot_config_cache.add_to_set("blacklist", "users", *user_ids)

    async def remove_blacklist(self, *user_ids: int) -> None:
        await self.bot_config_cache.pull("blacklist", "users", *user_ids)

    # message count

    async def get_message_count(self) -> int:
        document = await self.bot_config.find_one("stats", projection={"message_count": True, "_id": False})
        return document["message_count"]

    async def increase_message_count(self, amount: int) -> int:
        document = await self.bot_config.find_one_and_update(
            {"_id": "stats"},
            {"$inc": {"message_count": amount}},
            projection={"message_count": True, "_id": False},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return document["message_count"]

    # name history

    async def get_name_history(self, user_id: int) -> list[str]:
        document = await self.name_history.find_one(user_id)
        return document["names"] if document else []

    async def add_name_history(self, user_id: int, name: str) -> None:
        await self.name_history.update_one({"_id": user_id}, {"$push": {"names": name}}, upsert=True)
