import wx
from utils.translator import _
from utils.constants import APP_NAME, APP_VERSION_FULL, APP_DEV


class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=_("about.title"), size=(480, 400))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label=APP_NAME, style=wx.ALIGN_CENTER)
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        version = wx.StaticText(panel, label=_("about.version_label", version=APP_VERSION_FULL), style=wx.ALIGN_CENTER)
        sizer.Add(version, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        dev = wx.StaticText(panel, label=_("about.developer", dev=APP_DEV), style=wx.ALIGN_CENTER)
        sizer.Add(dev, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        desc = wx.StaticText(panel, label=_("about.description"), style=wx.ALIGN_CENTER)
        sizer.Add(desc, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        usage_title = wx.StaticText(panel, label=_("about.usage_title"), style=wx.ALIGN_CENTER)
        usage_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        usage_title.SetFont(usage_font)
        sizer.Add(usage_title, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        usage_items = [
            _("about.usage_tab"),
            _("about.usage_arrows"),
            _("about.usage_enter"),
            _("about.usage_space"),
            _("about.usage_esc"),
        ]
        for item in usage_items:
            text = wx.StaticText(panel, label=item, style=wx.ALIGN_CENTER)
            sizer.Add(text, 0, wx.ALIGN_CENTER | wx.BOTTOM, 2)
        sizer.AddStretchSpacer()
        btn_close = wx.Button(panel, wx.ID_OK, _("about.close"))
        sizer.Add(btn_close, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        panel.SetSizer(sizer)
        self.Centre()
