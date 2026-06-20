import ctypes
import ctypes.wintypes


def speak(text):
    try:
        dll = ctypes.windll.LoadLibrary("nvdaControllerClient64.dll")
        if dll.nvdaController_testIfRunning() == 0:
            dll.nvdaController_speakText(text)
            return
    except Exception:
        pass
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text, 1)
    except Exception:
        pass
