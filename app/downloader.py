import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

import httpx

MAX_BYTES = 100 * 1024 * 1024  # 100 MB
ALLOWED_SUFFIXES = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".webm"}


class DownloadError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


class UnsupportedFormatError(Exception):
    pass


def _suffix_from_url(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if not suffix:
        return ".mp3"
    if suffix not in ALLOWED_SUFFIXES:
        raise UnsupportedFormatError(f"Unsupported audio format: {suffix}")
    return suffix


@asynccontextmanager
async def download_to_temp(url: str):
    suffix = _suffix_from_url(url)
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()

    try:
        written = 0
        async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
            try:
                async with client.stream("GET", url) as resp:
                    if resp.status_code >= 400:
                        raise DownloadError(
                            f"Download failed: HTTP {resp.status_code}"
                        )
                    with tmp_path.open("wb") as fh:
                        async for chunk in resp.aiter_bytes():
                            written += len(chunk)
                            if written > MAX_BYTES:
                                raise FileTooLargeError(
                                    f"File exceeds {MAX_BYTES} bytes"
                                )
                            fh.write(chunk)
            except httpx.HTTPError as exc:
                raise DownloadError(str(exc)) from exc

        yield str(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
