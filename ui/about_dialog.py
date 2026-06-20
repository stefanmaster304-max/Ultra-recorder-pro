import wx
from utils.translator import _
from utils.constants import APP_NAME, APP_VERSION_FULL, APP_DEV


class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title=_("about.title"), size=(520, 420))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label=APP_NAME, style=wx.ALIGN_CENTER)
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)
        version = wx.StaticText(panel, label=_("app.version"), style=wx.ALIGN_CENTER)
        sizer.Add(version, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        dev = wx.StaticText(panel, label=APP_DEV, style=wx.ALIGN_CENTER)
        sizer.Add(dev, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        msg = wx.TextCtrl(
            panel,
            value=_("app.welcome_message"),
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(480, 200),
        )
        msg_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        msg.SetFont(msg_font)
        sizer.Add(msg, 1, wx.EXPAND | wx.ALL, 15)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        sizer.AddStretchSpacer()
        btn_close = wx.Button(panel, wx.ID_OK, _("about.close"))
        sizer.Add(btn_close, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        panel.SetSizer(sizer)
        self.Centre()
