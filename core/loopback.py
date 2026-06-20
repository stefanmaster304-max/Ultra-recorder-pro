import sounddevice as sd
import numpy as np
import threading


class LoopbackCapture:
    def __init__(self, sample_rate=48000, device=None):
        self.sample_rate = sample_rate
        self.device = device
        self.running = False
        self.paused = False
        self.thread = None
        self.stream = None
        self.buffer = []
        self._event = threading.Event()
        self._error = None

    def start(self):
        self.running = True
        self.paused = False
        self.buffer = []
        self._error = None
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
            self.thread.join(timeout=3)
            self.thread = None

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        self._event.set()

    def get_audio_data(self):
        if not self.buffer:
            return np.array([], dtype=np.float32)
        try:
            return np.concatenate(self.buffer)
        except ValueError:
            return np.array([], dtype=np.float32)

    @staticmethod
    def find_stereo_mix_device():
        devices = sd.query_devices()
        for d in devices:
            if d["max_input_channels"] > 0:
                name = d["name"].lower()
                if "mix" in name or "est\u00e9reo" in name or "stereo" in name or "loopback" in name:
                    return d["index"]
        return None

    def _capture_thread(self):
        try:
            target_device = self.device
            if target_device is None:
                target_device = self.find_stereo_mix_device()
            if target_device is None:
                target_device = sd.default.device[0]
            dev_info = sd.query_devices(target_device)
            self.sample_rate = int(dev_info["default_samplerate"])
            channels = min(2, dev_info["max_input_channels"])
            def callback(indata, frames, time_info, status):
                if self.running and not self.paused:
                    data = indata.copy()
                    if data.shape[1] == 1:
                        data = np.column_stack([data[:, 0], data[:, 0]])
                    elif data.shape[1] > 2:
                        data = data[:, :2]
                    self.buffer.append(data.astype(np.float32))
            self.stream = sd.InputStream(
                device=target_device,
                samplerate=self.sample_rate,
                channels=channels,
                callback=callback,
                dtype=np.float32,
                blocksize=1024,
            )
            self.stream.start()
            while self.running:
                self._event.wait(0.1)
        except Exception as e:
            self._error = str(e)
            self.running = False
