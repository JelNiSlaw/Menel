import aiohttp

from Menel.utils.errors import ImgurUploadError


async def _upload(field_name: str, file: bytes) -> str:
    form = aiohttp.FormData()
    form.add_field(field_name, file)

    async with aiohttp.request(
            'POST', 'https://api.imgur.com/3/upload', data=form,
            timeout=aiohttp.ClientTimeout(total=20)
    ) as r:
        json = await r.json()

    if json['success']:
        return json['data']['link']
    else:
        raise ImgurUploadError(json['status'], json['data']['error'])


async def upload_image(image: bytes) -> str:
    return await _upload('image', image)


async def upload_video(video: bytes) -> str:
    return await _upload('video', video)