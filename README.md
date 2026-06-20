# Ultra Recorder Pro v1.7.0 beta

An accessible audio recorder for screen reader users (NVDA, JAWS).

Developer: Stefan, Stefan Games Productions

## Features

- Record system audio (WASAPI loopback)
- Record microphone audio
- Mix both sources or record individually
- Automatically mute/unmute screen reader (NVDA/JAWS) during recording
- Export to WAV, MP3, Opus, FLAC, OGG
- Auto-updater with GitHub releases
- Multi-language (English, Portuguese, Spanish)
- Fully accessible with keyboard navigation (Tab, Arrows, Enter, Space)
- Voice announcements via NVDA Controller Client API

## How to Run

### From Source
1. Install Python 3.13+ (3.14 recommended)
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

### Compiled .exe (via PyInstaller)
1. Install PyInstaller: `pip install pyinstaller`
2. Build: `pyinstaller ultra_recorder_pro.spec`
3. Run: `dist\UltraRecorderPro.exe`

## How to Push to GitHub

1. Install Git from https://git-scm.com/
2. Open PowerShell in this folder
3. Run:
   ```
   git init
   git remote add origin https://github.com/stefanmaster304-max/Ultra-recorder-pro.git
   git add -A
   git commit -m "v1.7.0 beta - initial release"
   git push -u origin main
   ```

## How to Create a Release (for Auto-Updates)

1. Build the .exe with PyInstaller (see above)
2. Create a ZIP of the `dist\UltraRecorderPro\` folder
3. On GitHub, go to Releases → Create a new release
4. Tag: `v1.7.0`, upload the ZIP file
5. Update `resources/update.json` with the new version and download URL
6. Push the updated `update.json` to the main branch

## Keyboard Navigation

- Tab/Shift+Tab: Navigate between controls
- Arrow keys: Navigate lists and combo boxes
- Enter: Activate button / confirm
- Space: Toggle checkbox
- Esc: Close dialogs
- Alt+R: Start/Stop Recording
- Alt+C: Settings
- Alt+L: Language
- Alt+U: Check Updates
- Alt+A: About

## License

Proprietary - Stefan Games Productions
