import wx
import threading
import time
from pathlib import Path
from utils.translator import _, set_locale, get_translator
from utils.config import config
from utils.constants import APP_NAME, APP_VERSION_FULL, APP_DEV
from utils.sounds import play_startup, play_shutdown
from utils.announcer import speak
from utils.ffmpeg_handler import is_ffmpeg_available, download_ffmpeg
from core.engine import RecordingEngine, RecordingMode, EngineState
from core.encoder import save_recording
from core.devices import get_input_devices, get_output_devices
from ui.settings_dialog import SettingsDialog
from ui.about_dialog import AboutDialog
from ui.language_dialog import LanguageDialog
from updater.update_checker import check_for_updates


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title=f"{APP_NAME} {APP_VERSION_FULL}", size=(500, 420))
        self.engine = RecordingEngine()
        self.engine.set_on_state_change(self._on_engine_state)
        self._timer_running = False
        self._update_timer = None
        self._setup_ui()
        self._setup_accelerators()
        self._layout_buttons_idle()
        self.Centre()
        self.Show()
        self._post_init()

    def _setup_ui(self):
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.main_sizer)
        self.main_sizer.AddStretchSpacer(1)
        self.timer_text = wx.StaticText(self.panel, label="", style=wx.ALIGN_CENTER)
        font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.timer_text.SetFont(font)
        self.timer_text.Hide()
        self.main_sizer.Add(self.timer_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.btn_record = wx.Button(self.panel, wx.ID_ANY, _("main.start_recording"))
        self.btn_pause = wx.Button(self.panel, wx.ID_ANY, _("main.pause"))
        self.btn_stop = wx.Button(self.panel, wx.ID_ANY, _("main.stop_recording"))
        self.btn_settings = wx.Button(self.panel, wx.ID_ANY, _("main.settings"))
        self.btn_language = wx.Button(self.panel, wx.ID_ANY, _("main.language"))
        self.btn_updates = wx.Button(self.panel, wx.ID_ANY, _("main.check_updates"))
        self.btn_about = wx.Button(self.panel, wx.ID_ANY, _("main.about"))
        self.control_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_pause.Hide()
        self.btn_stop.Hide()
        self.control_sizer.Add(self.btn_record, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 4)
        self.control_sizer.Add(self.btn_pause, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 4)
        self.control_sizer.Add(self.btn_stop, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 4)
        self.control_sizer.Add(self.btn_settings, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 4)
        self.control_sizer.Add(self.btn_language, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 4)
        self.control_sizer.Add(self.btn_updates, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 4)
        self.control_sizer.Add(self.btn_about, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 4)
        self.main_sizer.Add(self.control_sizer, 0, wx.ALIGN_CENTER, 0)
        self.main_sizer.AddStretchSpacer(1)
        self.status_bar = wx.StatusBar(self)
        self.status_bar.SetStatusText(_("main.status_ready"))
        self.SetStatusBar(self.status_bar)
        self.btn_record.Bind(wx.EVT_BUTTON, self._on_record)
        self.btn_pause.Bind(wx.EVT_BUTTON, self._on_pause)
        self.btn_stop.Bind(wx.EVT_BUTTON, self._on_stop)
        self.btn_settings.Bind(wx.EVT_BUTTON, self._on_settings)
        self.btn_language.Bind(wx.EVT_BUTTON, self._on_language)
        self.btn_updates.Bind(wx.EVT_BUTTON, self._on_updates)
        self.btn_about.Bind(wx.EVT_BUTTON, self._on_about)
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _setup_accelerators(self):
        entries = [
            (wx.ACCEL_ALT, ord("R"), self.btn_record.GetId()),
            (wx.ACCEL_ALT, ord("C"), self.btn_settings.GetId()),
            (wx.ACCEL_ALT, ord("L"), self.btn_language.GetId()),
            (wx.ACCEL_ALT, ord("U"), self.btn_updates.GetId()),
            (wx.ACCEL_ALT, ord("A"), self.btn_about.GetId()),
        ]
        if self.btn_pause.IsShown():
            entries.append((wx.ACCEL_ALT, ord("P"), self.btn_pause.GetId()))
        self.SetAcceleratorTable(wx.AcceleratorTable(entries))

    def _post_init(self):
        play_startup()
        if config.get("auto_check_updates", True):
            threading.Thread(target=self._auto_check_updates, daemon=True).start()

    def _auto_check_updates(self):
        try:
            result = check_for_updates()
            if result and result.get("available"):
                wx.CallAfter(self._show_update_prompt, result)
        except Exception:
            pass

    def _layout_buttons_idle(self):
        self.btn_record.Show()
        self.btn_pause.Hide()
        self.btn_stop.Hide()
        self.timer_text.Hide()
        self.control_sizer.Layout()
        self._setup_accelerators()
        self.status_bar.SetStatusText(_("main.status_ready"))

    def _layout_buttons_recording(self):
        self.btn_record.Hide()
        self.btn_pause.Show()
        self.btn_pause.SetLabel(_("main.pause"))
        self.btn_stop.Show()
        self.timer_text.Show()
        self.control_sizer.Layout()
        self._setup_accelerators()
        self.SetTitle(_("app.recording_title", name=APP_NAME))

    def _layout_buttons_paused(self):
        self.btn_pause.SetLabel(_("main.resume"))
        self.control_sizer.Layout()
        self.SetTitle(f"{_('app.recording_title', name=APP_NAME)} - {_('main.status_paused', elapsed='')}")

    def _on_engine_state(self, state):
        if state == EngineState.IDLE:
            self._timer_running = False
            if self._update_timer:
                self._update_timer.Stop()
                self._update_timer = None
            self._layout_buttons_idle()
            self.btn_settings.Enable()
            self.btn_language.Enable()
            self.btn_updates.Enable()
            self.btn_about.Enable()
        elif state == EngineState.RECORDING:
            self.btn_settings.Disable()
            self.btn_language.Disable()
            self.btn_updates.Disable()
            self.btn_about.Disable()
            self._layout_buttons_recording()
            self._start_timer()
        elif state == EngineState.PAUSED:
            self._layout_buttons_paused()

    def _start_timer(self):
        self._timer_running = True
        self._update_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self._update_timer)
        self._update_timer.Start(200)

    def _on_timer(self, event):
        if not self._timer_running:
            return
        elapsed = self.engine.get_elapsed()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.timer_text.SetLabel(time_str)
        if self.engine.is_recording:
            self.status_bar.SetStatusText(_("main.status_recording", elapsed=time_str))
        elif self.engine.is_paused:
            self.status_bar.SetStatusText(_("main.status_paused", elapsed=time_str))

    def _on_record(self, event):
        mode = config.get("recording_mode", "both")
        if mode == "system":
            eng_mode = RecordingMode.SYSTEM
        elif mode == "microphone":
            eng_mode = RecordingMode.MICROPHONE
        else:
            eng_mode = RecordingMode.BOTH
        input_dev = config.get("input_device")
        output_dev = config.get("output_device")
        sample_rate = config.get("sample_rate", 48000)
        self.engine.start(mode=eng_mode, input_device=input_dev, output_device=output_dev, sample_rate=sample_rate)
        speak(_("main.recording_started"))

    def _on_pause(self, event):
        if self.engine.is_recording:
            self.engine.pause()
            speak(_("main.recording_paused"))
        elif self.engine.is_paused:
            self.engine.resume()
            speak(_("main.recording_resumed"))

    def _on_stop(self, event):
        system_data, mic_data = self.engine.stop()
        if system_data is None:
            return
        speak(_("main.recording_stopped"))
        self.status_bar.SetStatusText(_("main.status_stopped"))
        self._process_recording(system_data, mic_data)

    def _process_recording(self, system_data, mic_data):
        import numpy as np
        mode = config.get("recording_mode", "both")
        audio_format = config.get("audio_format", "MP3")
        quality = config.get("quality", "320k")
        sample_rate = config.get("sample_rate", 48000)
        if audio_format != "WAV" and not is_ffmpeg_available():
            dlg = wx.MessageDialog(self, _("errors.ffmpeg_missing"), APP_NAME, wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            wx.CallAfter(self._download_ffmpeg_and_save, system_data, mic_data, mode, audio_format, quality, sample_rate)
            return
        self._do_save(system_data, mic_data, mode, audio_format, quality, sample_rate)

    def _download_ffmpeg_and_save(self, system_data, mic_data, mode, audio_format, quality, sample_rate):
        success = download_ffmpeg()
        if success:
            self._do_save(system_data, mic_data, mode, audio_format, quality, sample_rate)
        else:
            dlg = wx.MessageDialog(self, _("errors.ffmpeg_failed"), APP_NAME, wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            self._do_save(system_data, mic_data, mode, "WAV", quality, sample_rate)

    def _do_save(self, system_data, mic_data, mode, audio_format, quality, sample_rate):
        try:
            filepath = save_recording(system_data, mic_data, mode, audio_format, quality, sample_rate)
            if filepath:
                msg = _("main.recording_saved", file=filepath.name)
                speak(msg)
                dlg = wx.MessageDialog(self, f"{msg}\n\n{filepath.parent}", APP_NAME, wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.status_bar.SetStatusText(_("main.status_ready"))
        except Exception as e:
            dlg = wx.MessageDialog(self, _("errors.generic", error=str(e)), APP_NAME, wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def _on_settings(self, event):
        dlg = SettingsDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.apply_settings()
        dlg.Destroy()

    def _on_language(self, event):
        dlg = LanguageDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            selected = dlg.get_selected()
            current = config.get("language", "en-US")
            if selected != current:
                config.set("language", selected)
                msg = _("language.restart_question")
                msg_dlg = wx.MessageDialog(self, _("language.restart_prompt") + f"\n\n{msg}", _("language.title"), wx.YES_NO | wx.ICON_QUESTION)
                if msg_dlg.ShowModal() == wx.ID_YES:
                    msg_dlg.Destroy()
                    import subprocess, sys
                    subprocess.Popen([sys.executable or sys.argv[0]])
                    self.Close()
                else:
                    msg_dlg.Destroy()
        dlg.Destroy()

    def _on_updates(self, event):
        from updater.update_checker import check_for_updates
        from updater.update_downloader import download_update
        from updater.update_installer import install_update
        from utils.constants import APP_VERSION
        self.status_bar.SetStatusText(_("updater.checking"))
        self.btn_updates.Disable()
        result = check_for_updates()
        self.btn_updates.Enable()
        if result is None:
            dlg = wx.MessageDialog(self, _("updater.error_network"), APP_NAME, wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            self.status_bar.SetStatusText(_("main.status_ready"))
            return
        if not result.get("available"):
            dlg = wx.MessageDialog(self, _("updater.already_latest", version=APP_VERSION), APP_NAME, wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.status_bar.SetStatusText(_("main.status_ready"))
            return
        self._show_update_prompt(result)

    def _show_update_prompt(self, result):
        changelog = "\n".join(result.get("changelog", []))
        msg = _("updater.new_version_msg", version=result["version"], changelog=changelog or _("updater.new_version_title"))
        dlg = wx.MessageDialog(self, msg, _("updater.new_version_title"), wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            self._perform_update(result)
        else:
            dlg.Destroy()

    def _perform_update(self, result):
        self.status_bar.SetStatusText(_("updater.downloading", progress=0))
        def progress_callback(pct):
            wx.CallAfter(self.status_bar.SetStatusText, _("updater.downloading", progress=pct))
        zip_path = download_update(result["download_url"], progress_callback)
        if zip_path is None:
            dlg = wx.MessageDialog(self, _("updater.error_network"), APP_NAME, wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.status_bar.SetStatusText(_("main.status_ready"))
            return
        self.status_bar.SetStatusText(_("updater.downloaded"))
        wx.Yield()
        success = install_update(zip_path)
        if success:
            dlg = wx.MessageDialog(self, _("updater.installed"), APP_NAME, wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.Close()
        else:
            dlg = wx.MessageDialog(self, _("updater.error_checksum"), APP_NAME, wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.status_bar.SetStatusText(_("main.status_ready"))

    def _on_about(self, event):
        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_close(self, event):
        if self.engine.is_active:
            self.engine.stop()
        self.timer_text.Hide()
        self.control_sizer.Layout()
        play_shutdown()
        self.Destroy()
