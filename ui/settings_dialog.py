import wx
import threading
from utils.translator import _
from utils.config import config
from utils.constants import SAMPLE_RATES, FORMATS
from core.devices import get_input_devices, get_output_devices, get_device_name, get_default_input_device, get_default_output_device


class SettingsDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=_("settings.title"), size=(500, 520))
        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._create_input_device_section(sizer)
        sizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.ALL, 10)
        self._create_output_device_section(sizer)
        sizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.ALL, 10)
        self._create_format_section(sizer)
        sizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.ALL, 10)
        self._create_misc_section(sizer)
        sizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.ALL, 10)
        self._create_buttons(sizer)
        self.panel.SetSizer(sizer)
        self._load_settings()
        self.Centre()

    def _create_input_device_section(self, sizer):
        box = wx.StaticBox(self.panel, label=_("settings.input_device"))
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.input_devices = get_input_devices()
        choices = [d["name"] for d in self.input_devices] if self.input_devices else [_("settings.no_input_devices")]
        self.input_combo = wx.ComboBox(self.panel, choices=choices, style=wx.CB_READONLY)
        if not self.input_devices:
            self.input_combo.Disable()
        box_sizer.Add(self.input_combo, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(box_sizer, 0, wx.EXPAND | wx.ALL, 5)

    def _create_output_device_section(self, sizer):
        box = wx.StaticBox(self.panel, label=_("settings.output_device"))
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.output_devices = get_output_devices()
        choices = [d["name"] for d in self.output_devices] if self.output_devices else [_("settings.no_output_devices")]
        self.output_combo = wx.ComboBox(self.panel, choices=choices, style=wx.CB_READONLY)
        if not self.output_devices:
            self.output_combo.Disable()
        box_sizer.Add(self.output_combo, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(box_sizer, 0, wx.EXPAND | wx.ALL, 5)

    def _create_format_section(self, sizer):
        grid = wx.FlexGridSizer(2, 2, 10, 10)
        grid.AddGrowableCol(1)
        grid.Add(wx.StaticText(self.panel, label=_("settings.sample_rate")), 0, wx.ALIGN_CENTER_VERTICAL)
        rate_choices = [f"{r} {_('settings.hz')}" for r in SAMPLE_RATES]
        self.rate_combo = wx.ComboBox(self.panel, choices=rate_choices, style=wx.CB_READONLY)
        grid.Add(self.rate_combo, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self.panel, label=_("settings.audio_format")), 0, wx.ALIGN_CENTER_VERTICAL)
        self.format_combo = wx.ComboBox(self.panel, choices=FORMATS, style=wx.CB_READONLY)
        grid.Add(self.format_combo, 0, wx.EXPAND)
        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)
        self.quality_label = wx.StaticText(self.panel, label=_("settings.quality"))
        self.quality_combo = wx.ComboBox(self.panel, style=wx.CB_READONLY)
        self.format_combo.Bind(wx.EVT_COMBOBOX, self._on_format_change)
        qsizer = wx.BoxSizer(wx.HORIZONTAL)
        qsizer.Add(self.quality_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        qsizer.Add(self.quality_combo, 1, wx.EXPAND)
        sizer.Add(qsizer, 0, wx.EXPAND | wx.ALL, 5)

    def _create_misc_section(self, sizer):
        self.tts_check = wx.CheckBox(self.panel, label=_("settings.include_tts"))
        sizer.Add(self.tts_check, 0, wx.ALL, 5)

    def _create_buttons(self, sizer):
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_test = wx.Button(self.panel, wx.ID_ANY, _("settings.test_mic"))
        self.btn_test.Bind(wx.EVT_BUTTON, self._on_test_mic)
        btn_sizer.Add(self.btn_test, 0, wx.RIGHT, 10)
        self.btn_save = wx.Button(self.panel, wx.ID_OK, _("settings.save"))
        self.btn_cancel = wx.Button(self.panel, wx.ID_CANCEL, _("settings.cancel"))
        btn_sizer.Add(self.btn_save, 0, wx.RIGHT, 10)
        btn_sizer.Add(self.btn_cancel, 0)
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

    def _on_format_change(self, event):
        fmt = self.format_combo.GetStringSelection()
        if fmt == "WAV":
            choices = ["16 bit", "24 bit", "32 bit"]
        elif fmt == "MP3":
            choices = ["128k", "192k", "256k", "320k"]
        elif fmt == "Opus":
            choices = ["64k", "96k", "128k", "192k", "256k"]
        elif fmt == "FLAC":
            choices = [str(i) for i in range(9)]
        elif fmt == "OGG":
            choices = [str(i) for i in range(-1, 11)]
        else:
            choices = []
        self.quality_combo.Clear()
        self.quality_combo.AppendItems(choices)
        if choices:
            self.quality_combo.SetSelection(0)

    def _load_settings(self):
        if self.input_devices:
            dev_id = config.get("input_device")
            for i, d in enumerate(self.input_devices):
                if d["index"] == dev_id or dev_id is None and i == 0:
                    self.input_combo.SetSelection(i)
                    break
            if self.input_combo.GetSelection() == wx.NOT_FOUND:
                self.input_combo.SetSelection(0)
        if self.output_devices:
            dev_id = config.get("output_device")
            for i, d in enumerate(self.output_devices):
                if d["index"] == dev_id or dev_id is None and i == 0:
                    self.output_combo.SetSelection(i)
                    break
            if self.output_combo.GetSelection() == wx.NOT_FOUND:
                self.output_combo.SetSelection(0)
        rate = config.get("sample_rate", 48000)
        rate_str = f"{rate} {_('settings.hz')}"
        for i, r in enumerate(SAMPLE_RATES):
            if f"{r} {_('settings.hz')}" == rate_str:
                self.rate_combo.SetSelection(i)
                break
        if self.rate_combo.GetSelection() == wx.NOT_FOUND:
            self.rate_combo.SetSelection(1)
        fmt = config.get("audio_format", "MP3")
        for i, f in enumerate(FORMATS):
            if f == fmt:
                self.format_combo.SetSelection(i)
                break
        if self.format_combo.GetSelection() == wx.NOT_FOUND:
            self.format_combo.SetSelection(1)
        self._on_format_change(None)
        quality = config.get("quality", "320k")
        for i in range(self.quality_combo.GetCount()):
            if self.quality_combo.GetString(i) == quality:
                self.quality_combo.SetSelection(i)
                break
        if self.quality_combo.GetSelection() == wx.NOT_FOUND and self.quality_combo.GetCount() > 0:
            last = self.quality_combo.GetCount() - 1
            self.quality_combo.SetSelection(last)
        self.tts_check.SetValue(config.get("include_tts", True))

    def apply_settings(self):
        if self.input_devices and self.input_combo.GetSelection() >= 0:
            idx = self.input_combo.GetSelection()
            config.set("input_device", self.input_devices[idx]["index"])
        if self.output_devices and self.output_combo.GetSelection() >= 0:
            idx = self.output_combo.GetSelection()
            config.set("output_device", self.output_devices[idx]["index"])
        rate_text = self.rate_combo.GetStringSelection()
        rate = int(rate_text.split()[0])
        config.set("sample_rate", rate)
        config.set("audio_format", self.format_combo.GetStringSelection())
        config.set("quality", self.quality_combo.GetStringSelection())
        config.set("include_tts", self.tts_check.GetValue())

    def _on_test_mic(self, event):
        self.btn_test.Disable()
        self.btn_test.SetLabel(_("mic_test.recording"))
        wx.Yield()
        import sounddevice as sd
        import numpy as np
        threading.Thread(target=self._do_mic_test, daemon=True).start()

    def _do_mic_test(self):
        import sounddevice as sd
        import numpy as np
        try:
            duration = 5
            sr = config.get("sample_rate", 48000)
            if self.input_devices and self.input_combo.GetSelection() >= 0:
                device = self.input_devices[self.input_combo.GetSelection()]["index"]
            else:
                device = None
            recording = sd.rec(int(duration * sr), samplerate=sr, channels=2, device=device, dtype=np.float32)
            sd.wait()
            wx.CallAfter(self.btn_test.SetLabel, _("mic_test.playing"))
            sd.play(recording * 0.5, sr)
            sd.wait()
            wx.CallAfter(self.btn_test.SetLabel, _("settings.test_mic"))
        except Exception:
            wx.CallAfter(self.btn_test.SetLabel, _("settings.test_mic"))
        wx.CallAfter(self.btn_test.Enable)
        from utils.announcer import speak
        speak(_("mic_test.done"))
