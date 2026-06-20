import comtypes
import comtypes.client
import ctypes
from ctypes import c_ulong, c_wchar_p, sizeof, c_void_p, POINTER as C_POINTER
from comtypes import GUID, POINTER, HRESULT, COMMETHOD
from comtypes.automation import VARIANT_BOOL

CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
IID_IMMDeviceEnumerator = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
IID_IAudioSessionManager2 = GUID("{77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F}")
IID_IAudioSessionControl2 = GUID("{BFB7FF88-0742-453E-AE0B-0E8CAAE35B5D}")
IID_ISimpleAudioVolume = GUID("{87CE5498-68D6-44E5-9215-6DA47EF883D1}")

_muted_sessions = []


def _get_nvda_pids():
    import psutil
    pids = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = proc.info["name"] or ""
            if name.lower() in ("nvda.exe", "jfw.exe", "jaws.exe"):
                pids.append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return pids


def mute_tts_sessions():
    global _muted_sessions
    _muted_sessions = []
    try:
        comtypes.CoInitialize()
        tts_pids = _get_nvda_pids()
        if not tts_pids:
            return
        enumerator = comtypes.client.CreateObject(CLSID_MMDeviceEnumerator, interface=IID_IMMDeviceEnumerator)
        device = enumerator.GetDefaultAudioEndpoint(0, 1)
        session_manager = device.Activate(IID_IAudioSessionManager2, 0, None)
        session_enum = session_manager.GetSessionEnumerator()
        count = session_enum.GetCount()
        for i in range(count):
            try:
                session = session_enum.GetSession(i)
                control2 = session.QueryInterface(IID_IAudioSessionControl2)
                pid = control2.GetProcessId()
                if pid in tts_pids:
                    volume = session.QueryInterface(IID_ISimpleAudioVolume)
                    volume.SetMute(True, None)
                    _muted_sessions.append(volume)
            except Exception:
                pass
        comtypes.CoUninitialize()
    except Exception:
        comtypes.CoUninitialize()


def unmute_tts_sessions():
    global _muted_sessions
    for volume in _muted_sessions:
        try:
            volume.SetMute(False, None)
        except Exception:
            pass
    _muted_sessions = []
