from typing import AsyncIterator, Optional

import aiohttp


class Downloader:
    def __init__(self, url: str) -> None:
        self._url = url
        self._content_length: Optional[int] = None

    @property
    def url(self) -> str:
        return self._url

    @property
    def content_length(self) -> Optional[int]:
        return self._content_length

    async def get_content_length(
        self,
        session: aiohttp.ClientSession,
    ) -> Optional[int]:
        async with session.head(self.url, allow_redirects=True) as response:
            content_length = response.headers.get("Content-Length")
            self._content_length = (
                int(content_length) if content_length is not None else None
            )
        return self._content_length

    async def read(
        self,
        session: aiohttp.ClientSession,
        chunk_size: int = 1024,
    ) -> AsyncIterator[bytes]:
        async with session.get(self.url, allow_redirects=True) as response:
            while True:
                chunk = await response.content.read(chunk_size)
                if not chunk:
                    break
                yield chunk
