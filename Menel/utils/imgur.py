from os import environ

import aiohttp

from Menel.utils.errors import ImgurUploadError


async def _upload(field_name: str, file: bytes) -> str:
    form = aiohttp.FormData()
    form.add_field(field_name, file)

    async with aiohttp.request(
            'POST', 'https://api.imgur.com/3/upload', data=form,
            headers={'Authorization': f"Client-ID {environ['IMGUR_CLIENT_ID']}"},
            timeout=aiohttp.ClientTimeout(total=20)
    ) as r:
        json = await r.json()

    if r.status == 200:
        return json['data']['link']
    else:
        raise ImgurUploadError(json.get('status', 0), json['data'].get('error', 'Nieznany błąd serwera Imgur'))


async def upload_image(image: bytes) -> str:
    return await _upload('image', image)


async def upload_video(video: bytes) -> str:
    return await _upload('video', video)