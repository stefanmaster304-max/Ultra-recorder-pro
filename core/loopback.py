import comtypes
import comtypes.client
import numpy as np
import threading
import time
from ctypes import c_uint16, c_uint32, c_void_p, sizeof, POINTER as C_POINTER, byref
from comtypes import GUID, POINTER, COMMETHOD, HRESULT

AUDCLNT_STREAMFLAGS_LOOPBACK = 0x00020000
AUDCLNT_STREAMFLAGS_EVENTCALLBACK = 0x00040000

CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
IID_IMMDeviceEnumerator = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
IID_IAudioClient = GUID("{1CB9AD4C-DBFA-4C32-B178-C2F568A703B2}")
IID_IAudioCaptureClient = GUID("{C8ADBD64-E71E-48A0-A4DE-185C395CD317}")


class WAVEFORMATEX(comtypes.Structure):
    _fields_ = [
        ("wFormatTag", c_uint16),
        ("nChannels", c_uint16),
        ("nSamplesPerSec", c_uint32),
        ("nAvgBytesPerSec", c_uint32),
        ("nBlockAlign", c_uint16),
        ("wBitsPerSample", c_uint16),
        ("cbSize", c_uint16),
    ]


class LoopbackCapture:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.running = False
        self.paused = False
        self.thread = None
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
        self._event.set()
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

    def _capture_thread(self):
        try:
            comtypes.CoInitialize()
            enumerator = comtypes.client.CreateObject(
                CLSID_MMDeviceEnumerator,
                interface=IID_IMMDeviceEnumerator
            )
            device = enumerator.GetDefaultAudioEndpoint(0, 1)
            audio_client = device.Activate(
                IID_IAudioClient,
                0,
                None
            )
            mix_format_ptr = audio_client.GetMixFormat()
            wf = comtypes.cast(mix_format_ptr, POINTER(WAVEFORMATEX))[0]
            self.sample_rate = wf.nSamplesPerSec
            buffer_duration = 200000
            audio_client.Initialize(
                0,
                AUDCLNT_STREAMFLAGS_LOOPBACK | AUDCLNT_STREAMFLAGS_EVENTCALLBACK,
                buffer_duration,
                0,
                mix_format_ptr,
                None
            )
            event_handle = comtypes.windll.kernel32.CreateEventW(None, 0, 0, None)
            audio_client.SetEventHandle(event_handle)
            capture_client = audio_client.GetService(IID_IAudioCaptureClient)
            audio_client.Start()
            while self.running:
                if self.paused:
                    self._event.wait(0.1)
                    continue
                if comtypes.windll.kernel32.WaitForSingleObject(event_handle, 2000) != 0:
                    continue
                while self.running:
                    packet_size = capture_client.GetNextPacketSize()
                    if packet_size == 0:
                        break
                    buffer_ptr, frames, flags, dev_pos, qpc = capture_client.GetBuffer()
                    if frames > 0 and buffer_ptr:
                        total_samples = frames * wf.nBlockAlign
                        raw_data = (c_void_p * total_samples).from_address(buffer_ptr)
                        if wf.wBitsPerSample == 32:
                            dtype = np.float32
                        elif wf.wBitsPerSample == 16:
                            dtype = np.int16
                        else:
                            dtype = np.int16
                        data = np.frombuffer(
                            bytearray(raw_data),
                            dtype=dtype,
                            count=frames * wf.nChannels
                        )
                        if dtype != np.float32:
                            data = data.astype(np.float32) / 32768.0
                        data = data.reshape(-1, wf.nChannels).copy()
                        if wf.nChannels == 1:
                            data = np.column_stack([data[:, 0], data[:, 0]])
                        elif wf.nChannels > 2:
                            data = data[:, :2]
                        self.buffer.append(data)
                    capture_client.ReleaseBuffer(frames)
            audio_client.Stop()
            comtypes.windll.kernel32.CloseHandle(event_handle)
            comtypes.CoUninitialize()
        except Exception as e:
            self._error = str(e)
            self.running = False
            try:
                comtypes.CoUninitialize()
            except Exception:
                pass
