from datetime import datetime
from os import getenv
from typing import List, Optional

import aiohttp

from ..functions import clean_content


class ImperialDocument:
    def __init__(self, data: dict):
        self.raw_link: str = data['rawLink']
        self.formatted_link: str = data['formattedLink']
        self.document_id: str = data['document']['documentId']
        self.language: str = data['document']['language']
        self.image_embed: bool = data['document']['imageEmbed']
        self.instant_delete: bool = data['document']['instantDelete']
        self.creation_date: datetime = datetime.utcfromtimestamp(data['document']['creationDate'] / 1000)
        self.expiration_date: datetime = datetime.utcfromtimestamp(data['document']['expirationDate'] / 1000)
        self.allowed_editors: List[str] = data['document']['allowedEditors']
        self.encrypted: bool = data['document']['encrypted']
        self.password: Optional[str] = data['document']['password']
        self.views: int = data['document']['views']


class ImperialException(Exception):
    pass


async def create_document(
    text: str,
    *,
    longer_urls: bool = True,
    language: str = 'plain_text',
    image_embed: bool = False,
    instant_delete: bool = False,
    password: Optional[str] = None,
    expiration: int = 1,
    editor_array: Optional[List[str]] = None
) -> ImperialDocument:
    async with aiohttp.request(
            'POST', 'https://imperialb.in/api/document',
            json={
                'code': clean_content(text, False, False, 128 * 1024),
                'longerUrls': longer_urls,
                'language': language,
                'imageEmbed': image_embed,
                'instantDelete': instant_delete,
                'encrypted': password is not None,
                'password': password,
                'expiration': expiration,
                'editorArray': editor_array
            },
            headers={'Authorization': getenv('IMPERIAL_TOKEN')},
            timeout=aiohttp.ClientTimeout(total=20)
    ) as r:
        json = await r.json()

    if not json['success']:
        raise ImperialException(json['message'])

    return ImperialDocument(json)