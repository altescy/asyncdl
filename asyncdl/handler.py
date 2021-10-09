import asyncio
from typing import BinaryIO, Optional, AsyncIterator, Union

import aiohttp

from asyncdl.downloader import Downloader
from asyncdl.progress import Progress, ProgressBar, MultiProgressBar


class DownloadHandler:
    SIZE_UNIT = "B"

    def __init__(
        self,
        url_or_downloader: Union[str, Downloader],
        output: BinaryIO,
    ) -> None:
        if not output.writable:
            raise ValueError("The given output is not writable.")
        if isinstance(url_or_downloader, str):
            url_or_downloader = Downloader(url_or_downloader)

        self._downloader = url_or_downloader
        self._output = output
        self._progresss: Optional[Progress] = None

    @property
    def downloader(self) -> Downloader:
        return self._downloader

    @property
    def progress(self) -> Progress:
        if self._progresss is None:
            raise RuntimeError("Progress was not set.")
        return self._progresss

    async def set_progress(self, session: aiohttp.ClientSession) -> None:
        content_length = await self._downloader.get_content_length(session)
        self._progresss = Progress(0, content_length, self.SIZE_UNIT)

    async def download(
        self,
        session: aiohttp.ClientSession,
        chunk_size: int = 1024,
    ) -> AsyncIterator[None]:
        async for chunk in self._downloader.read(session, chunk_size):
            self._output.write(chunk)
            self.progress.update(len(chunk))
            yield


async def multi_download(*handlers: DownloadHandler) -> None:
    async with aiohttp.ClientSession() as session:
        await asyncio.wait([x.set_progress(session) for x in handlers])

        bars = [
            ProgressBar(
                progress=x.progress,
                title=x.downloader.url,
            )
            for x in handlers
        ]
        with MultiProgressBar(bars) as multi_bar:

            async def download_with_bar(handler: DownloadHandler) -> None:
                async for _ in handler.download(session):
                    multi_bar.update()

            await asyncio.wait([download_with_bar(x) for x in handlers])
