import threading
import time
import numpy as np
from core.loopback import LoopbackCapture
from core.microphone import MicrophoneCapture
from core.mixer import mix_audio
from utils.config import config
from utils.wasapi_session import mute_tts_sessions, unmute_tts_sessions


class RecordingMode:
    SYSTEM = "system"
    MICROPHONE = "microphone"
    BOTH = "both"


class EngineState:
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"


class RecordingEngine:
    def __init__(self):
        self.state = EngineState.IDLE
        self.loopback = None
        self.microphone = None
        self._start_time = None
        self._elapsed = 0.0
        self._pause_start = None
        self._tts_muted = False
        self._state_lock = threading.Lock()
        self._on_state_change = None

    def set_on_state_change(self, callback):
        self._on_state_change = callback

    def _notify_state(self):
        if self._on_state_change:
            self._on_state_change(self.state)

    def start(self, mode=RecordingMode.BOTH, input_device=None, output_device=None, sample_rate=48000):
        with self._state_lock:
            if self.state != EngineState.IDLE:
                return
            self.state = EngineState.RECORDING
        include_tts = config.get("include_tts", True)
        if not include_tts and mode in (RecordingMode.SYSTEM, RecordingMode.BOTH):
            try:
                mute_tts_sessions()
                self._tts_muted = True
            except Exception:
                self._tts_muted = False
        if mode in (RecordingMode.SYSTEM, RecordingMode.BOTH):
            self.loopback = LoopbackCapture(sample_rate=sample_rate)
            self.loopback.start()
        if mode in (RecordingMode.MICROPHONE, RecordingMode.BOTH):
            self.microphone = MicrophoneCapture(device=input_device, sample_rate=sample_rate)
            self.microphone.start()
        self._start_time = time.time()
        self._elapsed = 0.0
        self._notify_state()

    def pause(self):
        with self._state_lock:
            if self.state != EngineState.RECORDING:
                return
            self.state = EngineState.PAUSED
            self._pause_start = time.time()
        if self.loopback:
            self.loopback.pause()
        if self.microphone:
            self.microphone.pause()
        self._notify_state()

    def resume(self):
        with self._state_lock:
            if self.state != EngineState.PAUSED:
                return
            self.state = EngineState.RECORDING
        if self._pause_start:
            self._start_time += time.time() - self._pause_start
            self._pause_start = None
        if self.loopback:
            self.loopback.resume()
        if self.microphone:
            self.microphone.resume()
        self._notify_state()

    def stop(self):
        with self._state_lock:
            if self.state not in (EngineState.RECORDING, EngineState.PAUSED):
                return None, None
            self.state = EngineState.STOPPED
        if self._tts_muted:
            try:
                unmute_tts_sessions()
            except Exception:
                pass
            self._tts_muted = False
        if self.loopback:
            self.loopback.stop()
        if self.microphone:
            self.microphone.stop()
        if self._start_time:
            if self._pause_start:
                self._elapsed += self._pause_start - self._start_time
            else:
                self._elapsed += time.time() - self._start_time
        system_data = self.loopback.get_audio_data() if self.loopback else np.array([], dtype=np.float32)
        mic_data = self.microphone.get_audio_data() if self.microphone else np.array([], dtype=np.float32)
        self.loopback = None
        self.microphone = None
        self._start_time = None
        self._pause_start = None
        self._elapsed = 0.0
        self.state = EngineState.IDLE
        self._notify_state()
        return system_data, mic_data

    def get_elapsed(self):
        with self._state_lock:
            if self.state == EngineState.IDLE:
                return 0.0
            elapsed = self._elapsed
            if self.state == EngineState.RECORDING and self._start_time:
                elapsed += time.time() - self._start_time
            return elapsed

    @property
    def is_recording(self):
        return self.state == EngineState.RECORDING

    @property
    def is_paused(self):
        return self.state == EngineState.PAUSED

    @property
    def is_active(self):
        return self.state in (EngineState.RECORDING, EngineState.PAUSED)
