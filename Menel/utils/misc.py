import time
from typing import Iterable, Optional, Union

import discord
from discord.ext import commands

from ..utils.context import Context


def clamp(val: int, minval: int, maxval: int):  # sourcery skip: min-max-identity
    return minval if val < minval else maxval if val > maxval else val


def chunk(iterator: Union[list, str], max_size: int) -> Iterable:
    for i in range(0, len(iterator), max_size):
        yield iterator[i : i + max_size]


def get_image_url_from_message(message: discord.Message) -> Optional[str]:
    if attachments := message.attachments:
        return attachments[0].url

    embeds = message.embeds
    if embeds:
        if embed := discord.utils.get(embeds, type="image"):
            return embed.url  # type: ignore

        if embed := discord.utils.find(lambda e: e.image.url, embeds):
            return embed.image.url  # type: ignore


async def get_image_url_from_message_or_reply(ctx: Context) -> Optional[str]:
    if url := get_image_url_from_message(ctx.message):
        return url

    if ref := ctx.message.reference:
        msg = ref.cached_message or await ctx.bot.fetch_message(ref.channel_id, ref.message_id)
        return get_image_url_from_message(msg)


class Timer:
    def __init__(self):
        self.time: Optional[float] = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.time = time.perf_counter() - self._start
