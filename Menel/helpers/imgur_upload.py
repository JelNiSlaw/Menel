import aiohttp


async def imgur_upload(image: bytes) -> dict:
    async with aiohttp.request(
            'POST', 'https://api.imgur.com/3/upload',
            data={'image': image, 'type': 'file'},
            timeout=aiohttp.ClientTimeout(total=10)
    ) as r:
        return await r.json()