import os
import sys
import zipfile
import tempfile
from pathlib import Path


def install_update(zip_path):
    try:
        base_dir = Path(sys.argv[0]).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent
        if getattr(sys, "frozen", False):
            _create_update_script(zip_path, base_dir)
        else:
            _install_dev_update(zip_path, base_dir)
        return True
    except Exception:
        return False


def _install_dev_update(zip_path, base_dir):
    import shutil
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            if member.startswith("__MACOSX") or member.startswith("."):
                continue
            target = base_dir / member
            if member.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as source, open(target, "wb") as dest:
                    dest.write(source.read())


def _create_update_script(zip_path, base_dir):
    bat_content = f"""@echo off
title Ultra Recorder Pro Updater
:wait
tasklist 2>nul | find /i "UltraRecorderPro.exe" >nul 2>nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul 2>nul
    goto wait
)
if exist "{base_dir}\\UltraRecorderPro_old.exe" del "{base_dir}\\UltraRecorderPro_old.exe" >nul 2>nul
if exist "{base_dir}\\UltraRecorderPro.exe" ren "{base_dir}\\UltraRecorderPro.exe" "UltraRecorderPro_old.exe" >nul 2>nul
copy /y "{zip_path}" "{base_dir}\\UltraRecorderPro.exe" >nul 2>nul
start "" /b "{base_dir}\\UltraRecorderPro.exe"
del "%~f0" >nul 2>nul
"""
    bat_path = base_dir / "_update_install.bat"
    with open(bat_path, "w") as f:
        f.write(bat_content)
    os.system(f'start "" /min "{bat_path}"')
