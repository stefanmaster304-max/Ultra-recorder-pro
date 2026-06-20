import wx
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils.config import config
from utils.translator import set_locale
from ui.main_frame import MainFrame


class UltraRecorderApp(wx.App):
    def OnInit(self):
        lang = config.get("language", "en-US")
        set_locale(lang)
        self.frame = MainFrame()
        self.SetTopWindow(self.frame)
        return True


def main():
    app = UltraRecorderApp(redirect=False)
    app.MainLoop()


if __name__ == "__main__":
    main()
