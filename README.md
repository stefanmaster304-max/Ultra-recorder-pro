# Ultra Recorder Pro v1.7.0 beta

**An intelligent audio recorder developed by blind people for blind people.**

Developer: Stefan, Stefan Games Productions

## Features

### Recording
- **System audio**: Captures all sounds played on your computer (games, music, videos, etc.) using Stereo Mix or WASAPI loopback.
- **Microphone**: Records from any connected microphone.
- **Mixed mode**: Records both system audio and microphone simultaneously and merges them into a single file.
- **Screen reader voice control**: Option to include or automatically exclude NVDA/JAWS voice from system audio recordings.

### Audio Quality
- Sample rates: 44100, 48000, 96000, 192000 Hz.
- Export formats: WAV (16/24/32-bit), MP3 (128-320 kbps), Opus (64-256 kbps), FLAC (compression 0-8), OGG Vorbis (quality -1 to 10).
- FFmpeg is bundled and ready to use.

### Accessibility
- Fully compatible with NVDA and JAWS screen readers.
- All controls are accessible via keyboard navigation.
- Voice announcements using NVDA Controller Client API (with SAPI fallback).
- Startup and shutdown audio cues.
- Multi-language support: English (default), Portuguese (Brazil), Spanish.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Alt + R | Start / Stop recording |
| Alt + C | Open Settings |
| Alt + L | Open Language selector |
| Alt + A | Open About dialog |
| Tab / Shift+Tab | Navigate between controls |
| Arrow keys | Navigate lists and combo boxes |
| Enter | Activate button / confirm |
| Space | Toggle checkbox |
| Esc | Close dialog |

## Recording Modes

Set in Settings > Recording mode:

1. **System audio only**: Records computer audio (games, music, etc.).
2. **Microphone only**: Records from microphone.
3. **System + Microphone (mix)**: Records both and merges into one file.

## Recording Process

1. Open Settings to select devices, format, and quality.
2. Click "Start Recording" (or press Alt+R).
3. Timer appears showing elapsed time.
4. Options: "Pause" to pause, "Stop" to finish.
5. File is automatically saved to `Downloads\Recordings\` with date/time name.

## Output Folder

Recordings are saved to: `%USERPROFILE%\Downloads\Recordings\`
File naming: `Recording_YYYY-MM-DD_HH-MM-SS.mp3` (format depends on settings)

## Requirements

- Windows 10 or 11 (64-bit).
- Stereo Mix or WASAPI loopback capable sound card (most modern ones).
- Microphone (optional, for microphone recording).

## How to Run

### From source:
```
pip install -r requirements.txt
python main.py
```

### Compiled with PyInstaller:
```
pip install pyinstaller
pyinstaller ultra_recorder_pro.spec
```

## External Dependencies

- **FFmpeg 8.1.1** (bundled as ffmpeg.exe) - used for audio format conversion (MP3, Opus, FLAC, OGG).
- **NVDA Controller Client DLL** (bundled as nvdaControllerClient64.dll) - used for screen reader announcements.

## About

Ultra Recorder Pro was created to provide a fully accessible audio recording solution for blind and visually impaired users who rely on screen readers like NVDA and JAWS.

Version 1.7.0 beta
Developer: Stefan, Stefan Games Productions
