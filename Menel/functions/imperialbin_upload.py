from os import getenv

import aiohttp


async def imperialbin_upload(
        text: str,
        *,
        longer_urls: bool = True,
        instant_delete: bool = False,
        image_embed: bool = True,
        expiration: int = 7,
) -> dict:
    async with aiohttp.request(
            'POST', 'https://imperialb.in/api/postCode/',
            json={
                'code': text,
                'apiToken': getenv('IMPERIALBIN_TOKEN'),
                'longerUrls': longer_urls,
                'instantDelete': instant_delete,
                'imageEmbed': image_embed,
                'expiration': expiration
            },
            headers={'User-Agent': 'Menel Discord Bot (https://github.com/JelNiSlaw/Menel)'},
            timeout=aiohttp.ClientTimeout(total=20)
    ) as r:
        return await r.json()