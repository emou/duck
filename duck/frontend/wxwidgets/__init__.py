from threading import Thread
try:
    import wx
except ImportError:
    raise FrontendInitializeError('Could not import wx. Is wxpython installed?')

from duck.frontend import BaseFrontend
from duck.errors import FrontendInitializeError
from duck.log import loggers
from gui.noname import MainWindow

logger = loggers.main
idle_logger = loggers.idle

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
            idle_logger.debug('waiting for idle')
            self.backend.idle_wait()
            idle_logger.debug('woke up!')
            wx.PostEvent(self.window, IdleEvent())
            self.backend.idle_wokeup()

    def stop(self):
        self.should_run = False

import traceback
def command(func):
    def decorated(self, *args, **kwargs):
        # Indicate that the idle handler should skip the event from the idle
        # thread on the next pass, because we would have taken care of the idle
        # changes here.
        self.skip_idle = True
        self.handle_changes(self.backend.noidle())
        logger.debug('after handle_changes')
        ret = func(self, *args, **kwargs)
        logger.debug('calling func ', func.__name__)
        logger.debug('Ha!')
        logger.debug(''.join(traceback.format_stack()))
        logger.debug('=================')
        logger.debug('=================')
        # XXX: Should optimize this.
        self.update_status()
        logger.debug('after update status.. going idle.')
        self.backend.idle()
        logger.debug('went idle')
        return ret
    return decorated

class DuckWindow(MainWindow):

    def __init__(self, *args, **kwargs):
        assert 'backend' in kwargs
        self.backend = kwargs.pop('backend')
        MainWindow.__init__(self, *args, **kwargs)

        self.skip_idle = False
        self.state = None

        self.idle_thread = IdleThread(self.backend, self)
        self.Connect(-1, -1, IdleEvent.IDLE_EVENT_ID, self.do_changes)
        self.idle_thread.start()

        self.progress_slider.SetValue(0)
        self.progress_slider.Bind(wx.EVT_SLIDER, self.do_seek)
        self.update_slider = True
        self.progress_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.update_progress)

        self.volume_slider.Bind(wx.EVT_SLIDER, self.do_volume_set)

        self.update_status()
        self.backend.idle()

    def update_progress(self, event):
        self.progress_slider.SetValue(self.progress_slider.GetValue() + 1)

    def handle_changes(self, changes):
        if changes:
            logger.debug(changes)
        self.update_status()

    # XXX: This is MPD-specific. Move it to the backend somehow?
    def do_changes(self, event):
        """
        Event handler for idle events (changes to MPD state).
        """
        logger.debug('got an event...')
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
        self.progress_slider.Enable(True)

    @command
    def do_stop(self, event):
        self.backend.stop()

    @command
    def do_next(self, event):
        logger.debug('do_next')
        self.backend.next()

    @command
    def do_seek(self, event):
        logger.debug(event.GetEventType())
        slider = event.GetEventObject()
        self.backend.seek(slider.GetValue())
        self.update_slider = False

    @command
    def do_volume_set(self, event):
        logger.debug(event.GetEventType())
        #slider = event.GetEventObject()
        #self.backend.setvol(slider.GetValue())
 
    def update_status(self):
        logger.debug('Updating status...')
        state = self.backend.get_status()['state']
        getattr(self, 'on_' + state)()
        self.state = state
        if state != 'stop':
            self.common_update()

    def common_update(self):
        logger.debug('elapsed time: %s' % self.backend.elapsed_time)
        if self.update_slider:
            self.progress_slider.SetRange(0, self.backend.time)
        else:
            self.update_slider = False
        self.progress_slider.SetValue(self.backend.elapsed_time)
        self.progress_timer.Start(1000, oneShot=False)

    def on_play(self):
        pass

    def on_stop(self):
        self.stop_timer()
        self.progress_slider.SetValue(0)
        self.progress_slider.Enable(False)

    def stop_timer(self):
        if self.progress_timer.IsRunning():
            self.progress_timer.Stop()

    def on_pause(self):
        self.progress_slider.Enable(False)
        self.stop_timer()
        self.progress_timer.Stop()


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
