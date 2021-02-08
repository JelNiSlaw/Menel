from os import getenv
from typing import Optional

import aiohttp

from . import cut_long_text


class ImperialbinPaste:
    def __init__(
            self,
            *,
            success: bool,
            document_id: str,
            raw_link: str,
            formatted_link: str,
            expires_in: int,
            instant_delete: bool
    ):
        self.success = success
        self.document_id = document_id
        self.raw_link = raw_link
        self.formatted_link = formatted_link
        self.expires_in = expires_in
        self.instant_delete = instant_delete


async def imperialbin_upload(
        text: str,
        *,
        longer_urls: bool = True,
        instant_delete: bool = False,
        image_embed: bool = True,
        expiration: int = 7,
        max_len: int = 2**16,
        language: Optional[str] = None
) -> ImperialbinPaste:
    async with aiohttp.request(
            'POST', 'https://imperialb.in/api/postCode/',
            json={
                'code': cut_long_text(text, max_len),
                'apiToken': getenv('IMPERIALBIN_TOKEN'),
                'longerUrls': longer_urls,
                'instantDelete': instant_delete,
                'imageEmbed': image_embed,
                'expiration': expiration
            },
            headers={'User-Agent': 'Menel Discord Bot (https://github.com/JelNiSlaw/Menel)'},
            timeout=aiohttp.ClientTimeout(total=20)
    ) as r:
        json = await r.json()

    paste = ImperialbinPaste(
        success=json['success'],
        document_id=json['documentId'],
        raw_link=json['rawLink'],
        formatted_link=json['formattedLink'],
        expires_in=json['expiresIn'],
        instant_delete=json['instantDelete']
    )

    if language:
        paste.formatted_link += f'?lang={language}'

    return paste