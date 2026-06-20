import os
from pathlib import Path

APP_NAME = "Ultra Recorder Pro"
APP_VERSION = "1.7.0"
APP_VERSION_SUFFIX = "beta"
APP_VERSION_FULL = f"{APP_VERSION} {APP_VERSION_SUFFIX}"
APP_DEV = "Stefan, Stefan Games Productions"
APP_GITHUB_REPO = "stefanmaster304-max/Ultra-recorder-pro"
APP_UPDATE_URL = f"https://raw.githubusercontent.com/{APP_GITHUB_REPO}/main/update.json"

BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESOURCES_DIR = BASE_DIR / "resources"
SOUNDS_DIR = RESOURCES_DIR / "sounds"
LOCALES_DIR = RESOURCES_DIR / "locales"
FFMPEG_DIR = Path(os.environ.get("APPDATA", "")) / APP_NAME / "ffmpeg"
FFMPEG_PATH = FFMPEG_DIR / "ffmpeg.exe"
CONFIG_DIR = Path(os.environ.get("APPDATA", "")) / APP_NAME
CONFIG_PATH = CONFIG_DIR / "config.json"
DOWNLOADS_DIR = Path(os.path.expanduser("~")) / "Downloads"
RECORDINGS_DIR = DOWNLOADS_DIR / "Recordings"

SAMPLE_RATES = [44100, 48000, 96000, 192000]
FORMATS = ["WAV", "MP3", "Opus", "FLAC", "OGG"]
FORMAT_EXTENSIONS = {"WAV": ".wav", "MP3": ".mp3", "Opus": ".opus", "FLAC": ".flac", "OGG": ".ogg"}
LANGUAGES = {"pt-BR": "Portugu\u00eas (Brasil)", "en-US": "English (US)", "es-ES": "Espa\u00f1ol"}

RECORDING_FILENAME_FORMAT = "Recording_{date}_{time}"
