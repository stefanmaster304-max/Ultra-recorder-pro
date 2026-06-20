import json
from .constants import LOCALES_DIR


class Translator:
    def __init__(self, locale="en-US"):
        self.locale = locale
        self.data = {}
        self.load()

    def load(self):
        path = LOCALES_DIR / f"{self.locale}.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (IOError, json.JSONDecodeError):
            fallback = LOCALES_DIR / "en-US.json"
            try:
                with open(fallback, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (IOError, json.JSONDecodeError):
                self.data = {}

    def get(self, key, **kwargs):
        parts = key.split(".")
        value = self.data
        try:
            for part in parts:
                value = value[part]
            if kwargs and isinstance(value, str):
                return value.format(**kwargs)
            return value
        except (KeyError, TypeError):
            return key


_translator_instance = None


def set_locale(locale):
    global _translator_instance
    _translator_instance = Translator(locale)


def get_translator():
    global _translator_instance
    return _translator_instance


def _(key, **kwargs):
    t = get_translator()
    if t is None:
        return key
    return t.get(key, **kwargs)
