import numpy as np


def mix_audio(system_audio, mic_audio, system_gain=0.7, mic_gain=0.3):
    if len(system_audio) == 0 and len(mic_audio) == 0:
        return np.array([], dtype=np.float32)
    if len(system_audio) == 0:
        return mic_audio * mic_gain
    if len(mic_audio) == 0:
        return system_audio * system_gain
    min_len = min(len(system_audio), len(mic_audio))
    if system_audio.ndim == 1:
        system_audio = system_audio.reshape(-1, 1)
    if mic_audio.ndim == 1:
        mic_audio = mic_audio.reshape(-1, 1)
    max_channels = max(system_audio.shape[1], mic_audio.shape[1])
    if system_audio.shape[1] < max_channels:
        system_audio = np.column_stack([system_audio, system_audio[:, :1]])
    if mic_audio.shape[1] < max_channels:
        mic_audio = np.column_stack([mic_audio, mic_audio[:, :1]])
    mixed = system_audio[:min_len] * system_gain + mic_audio[:min_len] * mic_gain
    peak = np.max(np.abs(mixed))
    if peak > 1.0:
        mixed = mixed / peak * 0.95
    return mixed
