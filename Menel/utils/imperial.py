import datetime
from os import environ
from typing import Optional

import httpx

from ..utils.text_tools import limit_length


class ImperialDocument:
    def __init__(self, data: dict):
        self.raw_link: str = data['rawLink']
        self.formatted_link: str = data['formattedLink']
        self.document_id: str = data['document']['documentId']
        self.language: str = data['document']['language']
        self.image_embed: bool = data['document']['imageEmbed']
        self.instant_delete: bool = data['document']['instantDelete']
        self.creation_date: datetime = datetime.datetime.utcfromtimestamp(data['document']['creationDate'] / 1000)
        self.expiration_date: datetime = datetime.datetime.utcfromtimestamp(data['document']['expirationDate'] / 1000)
        self.allowed_editors: list[str] = data['document']['allowedEditors']
        self.encrypted: bool = data['document']['encrypted']
        self.password: Optional[str] = data['document']['password']
        self.views: int = data['document']['views']


class ImperialException(Exception):
    pass


async def create_document(
        text: str,
        *,
        short_urls: bool = False,
        longer_urls: bool = False,
        language: str = 'plain_text',
        image_embed: bool = False,
        instant_delete: bool = False,
        password: str = None,
        expiration: int = 1,
        editor_array: list[str] = None
) -> ImperialDocument:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            'https://imperialb.in/api/document',
            json={
                'code': limit_length(text, max_length=128 * 1024),
                'shortUrls': short_urls,
                'longerUrls': longer_urls,
                'language': language,
                'imageEmbed': image_embed,
                'instantDelete': instant_delete,
                'encrypted': password is not None,
                'password': password,
                'expiration': expiration,
                'editorArray': editor_array
            },
            headers={'Authorization': environ['IMPERIAL_TOKEN']}, timeout=httpx.Timeout(20)
        )
        json = r.json()

    if not json['success']:
        raise ImperialException(json['message'])

    return ImperialDocument(json)