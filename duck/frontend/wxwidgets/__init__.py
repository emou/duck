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

    IDLE_EVENT_ID = wx.NewId()

    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(self.IDLE_EVENT_ID)

class IdleThread(Thread):
    """
    The thread that checks for MPD status change.
    """

    def __init__(self, backend, window):
        Thread.__init__(self)
        self.setDaemon(True)
        self.backend = backend
        self.window = window
        self.should_run = True

    def run(self):
        while(self.should_run):
            print 'waiting for idle'
            self.backend.idle_wait()
            print 'woke up!'
            wx.PostEvent(self.window, IdleEvent())
            self.backend.idle_wokeup()

    def stop(self):
        self.should_run = False

def command(func):
    def decorated(self, *args, **kwargs):
        # Indicate that the idle handler should skip the event from the idle
        # thread on the next pass, because we would have taken care of the idle
        # changes here.
        print 'Command %s ' % func.__name__[3:]
        self.skip_idle = True
        self.handle_changes(self.backend.noidle())
        ret = func(self, *args, **kwargs)
        self.backend.idle()
        return ret
    return decorated

class DuckWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        assert 'backend' in kwargs
        self.backend = kwargs.pop('backend')
        MainWindow.__init__(self, *args, **kwargs)
        self.idle_thread = IdleThread(self.backend, self)
        self.Connect(-1, -1, IdleEvent.IDLE_EVENT_ID, self.do_changes)
        self.idle_thread.start()
        self.skip_idle = False
        self.backend.idle()

    def handle_changes(self, changes):
        if changes:
            print changes

    # XXX: This is MPD-specific. Move it to the backend somehow?
    def do_changes(self, event):
        """
        Event handler for idle events (changes to MPD state).
        """
        print 'got an event...'
        if not self.skip_idle:
            self.handle_changes(self.backend.noidle())
            self.backend.idle()
        self.skip_idle = False

    @command
    def do_previous(self, event):
        self.backend.previous()

    @command
    def do_play(self, event):
        self.backend.play()

    @command
    def do_stop(self, event):
        self.backend.stop()

    @command
    def do_next(self, event):
        print 'do_next'
        self.backend.next()

    @command
    def do_seek(self, event):
        position = event.GetPosition()
        self.backend.seek(position)

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
