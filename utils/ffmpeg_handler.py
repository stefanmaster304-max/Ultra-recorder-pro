from .constants import FFMPEG_PATH, BASE_DIR


def is_ffmpeg_available():
    if FFMPEG_PATH.exists():
        return True
    alt_path = BASE_DIR / "ffmpeg" / "ffmpeg.exe"
    if alt_path.exists():
        return True
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return True
    except Exception:
        return False
