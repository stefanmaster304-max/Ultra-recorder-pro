import os
import zipfile
import io
import requests
from .constants import FFMPEG_DIR, FFMPEG_PATH


FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_FILENAME = "ffmpeg.exe"


def is_ffmpeg_available():
    return FFMPEG_PATH.exists()


def _get_ffmpeg_download_progress(url):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        return response, total
    except requests.RequestException:
        return None, 0


def download_ffmpeg(progress_callback=None):
    try:
        FFMPEG_DIR.mkdir(parents=True, exist_ok=True)
        response, total = _get_ffmpeg_download_progress(FFMPEG_URL)
        if response is None:
            return False
        chunk_size = 8192
        downloaded = 0
        buffer = io.BytesIO()
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                buffer.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total > 0:
                    progress_callback(int(downloaded * 100 / total))
        buffer.seek(0)
        with zipfile.ZipFile(buffer) as zf:
            for name in zf.namelist():
                if name.endswith(FFMPEG_FILENAME):
                    with zf.open(name) as source, open(FFMPEG_PATH, "wb") as target:
                        target.write(source.read())
                    break
        os.chmod(FFMPEG_PATH, 0o755)
        return True
    except Exception:
        return False
