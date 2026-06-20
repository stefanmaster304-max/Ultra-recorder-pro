# Ultra Recorder Pro v1.7.0 beta

Audio recorder for screen reader users (NVDA, JAWS).

Developer: Stefan, Stefan Games Productions

## Features

- Record system audio (WASAPI loopback)
- Record microphone audio
- Mix both or record individually
- Auto-mute NVDA/JAWS during recording
- Export to WAV, MP3, Opus, FLAC, OGG
- Multi-language (English, Portuguese, Spanish)
- Fully keyboard accessible (Tab, Arrows, Enter)
- Voice announcements via NVDA API

## How to Run

```
python main.py
```

Or compile with PyInstaller:
```
pip install pyinstaller
pyinstaller ultra_recorder_pro.spec
```

## Keyboard Shortcuts

- Alt+R: Start/Stop Recording
- Alt+C: Settings
- Alt+L: Language
- Alt+A: About
