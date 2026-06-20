import wave
import struct
import numpy as np
import subprocess
import tempfile
from pathlib import Path
from utils.constants import RECORDINGS_DIR, FORMAT_EXTENSIONS, RECORDING_FILENAME_FORMAT, FFMPEG_PATH
from datetime import datetime


def _ensure_recordings_dir():
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


def _save_wav(filepath, data, sample_rate, bits_per_sample=16):
    data = np.asarray(data, dtype=np.float32)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    if bits_per_sample == 16:
        dtype = np.int16
        scale = 32767
        sampwidth = 2
    elif bits_per_sample == 24:
        dtype = np.int32
        scale = 8388607
        sampwidth = 3
    elif bits_per_sample == 32:
        dtype = np.int32
        scale = 2147483647
        sampwidth = 4
    else:
        dtype = np.int16
        scale = 32767
        sampwidth = 2
    data = (data * scale).clip(-scale - 1, scale).astype(dtype)
    with wave.open(str(filepath), "wb") as wf:
        wf.setnchannels(data.shape[1])
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())


def _get_ffmpeg():
    if FFMPEG_PATH.exists():
        return str(FFMPEG_PATH)
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return "ffmpeg"
    except Exception:
        return None


def _convert_with_ffmpeg(input_path, output_path, audio_format, quality, sample_rate):
    ffmpeg = _get_ffmpeg()
    if ffmpeg is None:
        raise RuntimeError("FFmpeg not available")
    cmd = [ffmpeg, "-y", "-i", str(input_path)]
    if audio_format == "MP3":
        cmd.extend(["-c:a", "libmp3lame", "-b:a", quality, "-ar", str(sample_rate)])
    elif audio_format == "Opus":
        cmd.extend(["-c:a", "libopus", "-b:a", quality, "-ar", str(sample_rate), "-vbr", "on"])
    elif audio_format == "FLAC":
        cmd.extend(["-c:a", "flac", "-compression_level", str(quality), "-ar", str(sample_rate)])
    elif audio_format == "OGG":
        cmd.extend(["-c:a", "libvorbis", "-q:a", str(quality), "-ar", str(sample_rate)])
    cmd.append(str(output_path))
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr.decode('utf-8', errors='ignore')}")


def save_recording(system_data, mic_data, mode="both", audio_format="MP3", quality="320k", sample_rate=48000):
    from core.mixer import mix_audio
    _ensure_recordings_dir()
    if mode == "system":
        audio = system_data if len(system_data) > 0 else np.array([], dtype=np.float32)
    elif mode == "microphone":
        audio = mic_data if len(mic_data) > 0 else np.array([], dtype=np.float32)
    else:
        audio = mix_audio(system_data, mic_data)
    if len(audio) == 0:
        return None
    if audio.ndim == 0:
        audio = audio.reshape(1)
    if audio.ndim == 1:
        audio = audio.reshape(-1, 1)
    now = datetime.now()
    filename_base = now.strftime(RECORDING_FILENAME_FORMAT)
    ext = FORMAT_EXTENSIONS.get(audio_format, ".wav")
    counter = 1
    filepath = RECORDINGS_DIR / f"{filename_base}{ext}"
    while filepath.exists():
        filepath = RECORDINGS_DIR / f"{filename_base}_{counter}{ext}"
        counter += 1
    if audio_format == "WAV":
        bits = 16
        if quality in ("16 bit", "24 bit", "32 bit"):
            bits = int(quality.split()[0])
        _save_wav(filepath, audio, sample_rate, bits)
    else:
        temp_wav = RECORDINGS_DIR / f"__temp_{filename_base}.wav"
        try:
            _save_wav(temp_wav, audio, sample_rate, 16)
            _convert_with_ffmpeg(temp_wav, filepath, audio_format, quality, sample_rate)
        finally:
            if temp_wav.exists():
                temp_wav.unlink()
    return filepath
