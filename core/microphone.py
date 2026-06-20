import sounddevice as sd
import numpy as np
import threading


class MicrophoneCapture:
    def __init__(self, device=None, sample_rate=48000, channels=2):
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.running = False
        self.paused = False
        self.thread = None
        self.stream = None
        self.buffer = []
        self._event = threading.Event()

    def start(self):
        self.running = True
        self.paused = False
        self.buffer = []
        self.thread = threading.Thread(target=self._capture_thread, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        self._event.set()

    def get_audio_data(self):
        if not self.buffer:
            return np.array([], dtype=np.float32)
        return np.concatenate(self.buffer)

    def _capture_thread(self):
        try:
            def callback(indata, frames, time_info, status):
                if self.running and not self.paused:
                    data = indata.copy()
                    if data.shape[1] == 1:
                        data = np.column_stack([data[:, 0], data[:, 0]])
                    elif data.shape[1] > 2:
                        data = data[:, :2]
                    self.buffer.append(data)
            self.stream = sd.InputStream(
                device=self.device,
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
                dtype=np.float32,
                blocksize=1024,
            )
            self.stream.start()
            while self.running:
                self._event.wait(0.1)
        except Exception:
            self.running = False
