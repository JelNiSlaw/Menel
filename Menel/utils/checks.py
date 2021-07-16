from typing import Callable, Optional

from discord.ext import commands

from ..utils.context import Context
from .errors import BadAttachmentCount, BadAttachmentType


def has_attachments(count: Optional[int] = None, allowed_types: Optional[tuple[str]] = None) -> Callable:
    @commands.check
    async def predicate(ctx: Context) -> bool:
        attachments = ctx.message.attachments
        if count is None:
            if not attachments:
                raise BadAttachmentCount(count)
        elif len(attachments) != count:
            raise BadAttachmentCount(count)

        if allowed_types is not None:
            for a in attachments:
                if a.content_type is None or not a.content_type.startswith(allowed_types):
                    raise BadAttachmentType(str(a.content_type))

        return True

    return predicate
