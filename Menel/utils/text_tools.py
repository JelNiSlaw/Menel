from typing import Any, Optional

import discord
from discord.ext import commands

from ..utils.formatting import bold


def clean_content(
        content: str,
        markdown: bool = True,
        mentions: bool = True,
        /, *,
        max_length: Optional[int] = None,
        max_lines: Optional[int] = None,
        end: str = '…'
) -> str:
    if markdown:
        content = discord.utils.escape_markdown(content, ignore_links=False)
    if mentions:
        content = discord.utils.escape_mentions(content)

    shortened = False

    if max_lines is not None and len(content.splitlines()) > max_lines:
        content = '\n'.join(content.splitlines()[:max_lines])
        shortened = True

    if max_length is not None and len(content) > max_length:
        content = content[:max_length - len(end)]
        shortened = True

    if shortened:
        content = content.rstrip() + end

    return content


def plural(count: int, one: str, few: str, many: str) -> str:
    if count == 1:
        word = one
    elif 10 <= count < 20:
        word = many
    else:
        word = few if 1 < count % 10 < 5 else many
    return f'{count:,} {word}'


def plural_time(number: int) -> str:
    if number >= 3600:
        number //= 3600
        unit = 'godzin'
    elif number >= 60:
        number //= 60
        unit = 'minut'
    else:
        unit = 'sekund'

    return plural(number, one=unit + 'ę', few=unit + 'y', many=unit)


# based on https://stackoverflow.com/a/1094933/11619130
def human_size(num: int, suffix: str = 'B') -> str:
    for unit in '', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi':
        if abs(num) < 1024:
            break
        num /= 1024

    return f'{num:,.1f} {unit}{suffix}'


def escape_str(text: str) -> str:
    return repr(text)[1:-1]


def name_id(obj: discord.abc.Snowflake) -> str:
    return f'{obj} ({obj.id})'


def ctx_location(ctx: commands.Context) -> str:
    return location(ctx.author, ctx.channel, ctx.guild)


def location(author: discord.abc.User, channel: discord.abc.Messageable, guild: Optional[discord.Guild]) -> str:
    text = f'@{author} in #{channel}'
    if guild is not None:
        text += f" in {guild}"
    return text


def user_input(text: Any) -> str:
    return bold(clean_content(str(text), max_length=32, max_lines=1))


def str_permissions(permissions: list[str]) -> str:
    return ', '.join(perm.replace('_', ' ') for perm in permissions)