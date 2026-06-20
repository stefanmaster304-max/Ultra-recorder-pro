import numpy as np
import sounddevice as sd
import threading

SAMPLE_RATE = 44100


def _generate_tone(frequency, duration, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * frequency * t) * 0.3


def _apply_envelope(signal, sample_rate=SAMPLE_RATE):
    length = len(signal)
    fade = min(int(sample_rate * 0.02), length // 4)
    if fade > 0:
        envelope = np.ones(length)
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        signal = signal * envelope
    return signal


def _build_startup():
    c5 = _generate_tone(523.25, 0.1)
    e5 = _generate_tone(659.25, 0.1)
    g5 = _generate_tone(783.99, 0.15)
    chord_len = min(len(c5), len(e5), len(g5))
    chord = (c5[:chord_len] * 0.15 + e5[:chord_len] * 0.15 + g5[:chord_len] * 0.15)
    signal = np.concatenate([c5, e5, chord])
    return _apply_envelope(signal)


def _build_shutdown():
    g5 = _generate_tone(783.99, 0.12)
    e5 = _generate_tone(659.25, 0.12)
    c5 = _generate_tone(523.25, 0.12)
    c4 = _generate_tone(261.63, 0.25)
    signal = np.concatenate([g5, e5, c5, c4])
    return _apply_envelope(signal)


def play_startup():
    threading.Thread(target=lambda: sd.play(_build_startup(), SAMPLE_RATE), daemon=True).start()


def play_shutdown():
    sd.play(_build_shutdown(), SAMPLE_RATE)
    sd.wait()
