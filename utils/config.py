import json
from .constants import CONFIG_DIR, CONFIG_PATH

DEFAULT_CONFIG = {
    "language": "en-US",
    "input_device": None,
    "output_device": None,
    "sample_rate": 48000,
    "audio_format": "MP3",
    "quality": "320k",
    "include_tts": True,
    "auto_check_updates": True,
    "recording_mode": "both",
}


class Config:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
        except (json.JSONDecodeError, IOError):
            pass

    def save(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def reset(self):
        self.data = dict(DEFAULT_CONFIG)
        self.save()


config = Config()
