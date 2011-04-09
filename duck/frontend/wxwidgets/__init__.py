from threading import Thread
try:
    import wx
except ImportError:
    raise FrontendInitializeError('Could not import wx. Is wxpython installed?')

from duck.frontend import BaseFrontend
from duck.errors import FrontendInitializeError
from gui.noname import MainWindow

class IdleEvent(wx.PyEvent):
    """
    An event representing an MPD status change.
    """

    EVT_RESULT_ID = wx.NewId()

    def __init__(self, changes):
        self.changes = changes
        wx.PyEvent.__init__(self)
        self.SetEventType(self.EVT_RESULT_ID)


class IdleThread(Thread):
    def __init__(self, frontend):
        pass

    def run(self):
        while(True):
            pass

class DuckWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        assert 'backend' in kwargs
        self.backend = kwargs.pop('backend')
        MainWindow.__init__(self, *args, **kwargs)
        self.backend.idle()

    def do_previous(self, event):
        backend.previous()

    def do_play(self, event):
        backend.play()

    def do_stop(self, event):
        backend.stop()

    def do_next(self, event):
        backend.next()

    def do_seek(self, event):
        position = event.GetPosition()
        backend.seek(position)

class Frontend(BaseFrontend):
    """
    A frontend, implemented using wxwidgets.
    """

    def run(self):
        """
        Initialize the wxWidgets system, create an application and start the main loop.
        """
        self.application = wx.App()
        self.main_window = DuckWindow(None, backend=self.backend)
        self.main_window.Show()
        self.application.SetTopWindow(self.main_window)
        return self.application.MainLoop()
