from os import environ

import httpx

from ..utils.errors import ImgurUploadError


async def _upload(filename: str, file: bytes) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.imgur.com/3/upload",
            files={filename: file},
            headers={"Authorization": f"Client-ID {environ['IMGUR_CLIENT_ID']}"},
        )
        json = r.json()

    if r.status_code == 200:
        return json["data"]["link"]
    else:
        raise ImgurUploadError(json.get("status", 0), json["data"].get("error", "Nieznany błąd serwera Imgur"))


async def upload_image(image: bytes) -> str:
    return await _upload("image", image)


async def upload_video(video: bytes) -> str:
    return await _upload("video", video)
