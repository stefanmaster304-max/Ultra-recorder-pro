import requests
import tempfile
from pathlib import Path


def download_update(url, progress_callback=None):
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        chunk_size = 8192
        downloaded = 0
        suffix = Path(url).suffix or ".zip"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total > 0:
                        progress_callback(int(downloaded * 100 / total))
            return Path(f.name)
    except (requests.RequestException, IOError):
        return None
