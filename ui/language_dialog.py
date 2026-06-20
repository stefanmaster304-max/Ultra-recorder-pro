import wx
from utils.translator import _
from utils.constants import LANGUAGES
from utils.config import config


class LanguageDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=_("language.title"), size=(350, 250))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        prompt = wx.StaticText(panel, label=_("language.prompt"))
        sizer.Add(prompt, 0, wx.ALL, 15)
        self.radio_box = wx.RadioBox(
            panel,
            label="",
            choices=list(LANGUAGES.values()),
            style=wx.RA_VERTICAL,
        )
        current = config.get("language", "en-US")
        keys = list(LANGUAGES.keys())
        for i, k in enumerate(keys):
            if k == current:
                self.radio_box.SetSelection(i)
                break
        sizer.Add(self.radio_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        sizer.AddStretchSpacer()
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_ok = wx.Button(panel, wx.ID_OK, _("language.yes"))
        self.btn_cancel = wx.Button(panel, wx.ID_CANCEL, _("language.no"))
        btn_sizer.Add(self.btn_ok, 0, wx.RIGHT, 10)
        btn_sizer.Add(self.btn_cancel)
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        panel.SetSizer(sizer)
        self.Centre()

    def get_selected(self):
        keys = list(LANGUAGES.keys())
        sel = self.radio_box.GetSelection()
        if 0 <= sel < len(keys):
            return keys[sel]
        return "en-US"
