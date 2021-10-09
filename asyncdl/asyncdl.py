import asyncio
from typing import Tuple

from asyncdl.handler import DownloadHandler, multi_download


def download_files(*ios: Tuple[str, str]) -> None:
    handlers = [DownloadHandler(url, open(filename, "wb")) for url, filename in ios]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(multi_download(*handlers))
