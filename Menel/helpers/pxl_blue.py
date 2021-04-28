from os import getenv
from typing import Optional

import aiohttp


class PxlBlueUpload:
    def __init__(self, data: dict):
        self.image: dict = data['image']
        self.url: str = data['url']
        self.raw_url: str = data['rawUrl']
        self.deletion_url: str = data['deletionUrl']


class PxlBlueException(Exception):
    pass


async def upload(
    file: bytes,
    filename: str,
    *,
    content_type: Optional[str] = None,
    host: str = 'i.pxl.blue'
) -> PxlBlueUpload:
    if '.' not in filename:
        filename += '.bin'

    form = aiohttp.FormData()
    form.add_field('file', file, filename=filename, content_type=content_type or 'application/octet-stream')
    form.add_field('host', host)
    form.add_field('key', getenv('PXL_BLUE_KEY'))

    async with aiohttp.request(
            'POST', 'https://api.pxl.blue/upload/extra',
            data=form,
            timeout=aiohttp.ClientTimeout(total=20)
    ) as r:
        json = await r.json()

    if not json.get('success'):
        raise PxlBlueException(json.get('message', 'Na pxl.blue wystąpił błąd'))

    return PxlBlueUpload(json)