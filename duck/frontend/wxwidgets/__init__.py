try:
    import wx
except ImportError:
    raise FrontendInitializeError('Could not import wx. Is wxpython installed?')

from threading import Thread

from duck.frontend import BaseFrontend
from duck.errors import FrontendInitializeError
from duck.log import loggers
from gui.noname import MainWindow

logger = loggers.main
idle_logger = loggers.idle
status_logger = loggers.status


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


class WindowUpdater(object):
    '''
    An object that updates the window based on changes.
    '''

    updates = set([
        'progress_slider',
        'volume_slider',
    ])

    def __init__(self, win):
        self.win = win
        self.state = None

    def update(self, skip_updates=None):
        self.common_update()
        for u in self.updates - set(skip_updates or []):
            getattr(self, 'update_' + u)()

    def update_progress_slider(self):
        self.win.progress_slider.SetRange(0, self.win.backend.time)
        self.win.progress_slider.SetValue(self.win.backend.elapsed_time)

    def update_volume_slider(self):
        self.win.volume_slider.SetValue(self.win.backend.volume)

    def update_progress(self, event):
        self.win.progress_slider.SetValue(self.win.progress_slider.GetValue() + 1)

    def update_status(self, skip_updates=None, changes=None):
        status_logger.debug('[update_status]')
        state = self.win.backend.get_status()['state']
        getattr(self.win.handler, 'on_' + state)()
        self.state = state
        if changes and 'playlist' in changes:
            self.reload_playlist()
        if state != 'stop':
            self.win.updater.update(skip_updates)

    def reload_playlist(self):
        pl = self.win.playlist
        pl.DeleteAllItems()
        for row, song in enumerate(self.win.backend.playlist.songs):
            item = wx.ListItem()
            item.SetData(long(song.id))
            idx = pl.InsertItem(item)
            pl.SetStringItem(idx, 0, str(song.pos))
            pl.SetStringItem(idx, 1, song.artist)
            pl.SetStringItem(idx, 2, song.title)
            pl.SetStringItem(idx, 3, str(song.time))

    def common_update(self):
        status_logger.debug('[common_update]')
        song = self.win.backend.current_song
        self.win.SetTitle('%s - %s' % (song.artist, song.title))
        self.win.progress_timer.Start(1000, oneShot=False)


class EventHandler(object):
    '''
    An object that handles window events.
    '''

    def __init__(self, win):
        self.win = win

    def on_play(self):
        self.win.progress_slider.Enable(True)

    def on_stop(self):
        self.stop_timer()
        self.win.progress_slider.SetValue(0)
        self.win.progress_slider.Enable(False)

    def stop_timer(self):
        if self.win.progress_timer.IsRunning():
            self.win.progress_timer.Stop()

    def on_pause(self):
        self.win.progress_slider.Enable(False)
        self.stop_timer()
        self.win.progress_timer.Stop()


class Command(object):
    def __init__(self, skip_updates=None):
        self.skip_updates = skip_updates

    def __call__(self, func):
        def decorated(win, *args, **kwargs):
            status_logger.debug('[%s command begin]' % func.__name__)

            # Indicate that the idle handler should skip the event from the idle
            # thread on the next pass, because we would have taken care of the idle
            # changes here.
            win.skip_idle = True
            win.handle_changes(win.backend.noidle(), self.skip_updates)
            logger.debug('after handle_changes')

            # call the actual method
            ret = func(win, *args, **kwargs)

            win.backend.idle()
            idle_logger.debug('went idle')

            status_logger.debug('[%s command end]' % func.__name__)
            return ret
        return decorated


class DuckWindow(MainWindow):

    def __init__(self, *args, **kwargs):
        assert 'backend' in kwargs
        self.backend = kwargs.pop('backend')
        MainWindow.__init__(self, *args, **kwargs)

        for (i,col) in enumerate((('Pos',       50),
                                  ('Artist',    200),
                                  ('Title',     200),
                                  ('Duration',  100))):
            self.playlist.InsertColumn(i, col[0], width=col[1])
        self.playlist.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.do_change_song)

        self.skip_idle = False
        self.updater = WindowUpdater(self)
        self.handler = EventHandler(self)

        self.idle_thread = IdleThread(self.backend, self)
        self.Connect(-1, -1, IdleEvent.IDLE_EVENT_ID, self.handle_idle)
        self.idle_thread.start()

        self.progress_slider.SetValue(0)
        self.progress_slider.Bind(wx.EVT_SLIDER, self.do_seek)
        self.progress_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.updater.update_progress)

        self.volume_slider.Bind(wx.EVT_SLIDER, self.do_volume_set)

        self.updater.update_status()
        self.updater.reload_playlist()
        self.backend.idle()

    def handle_changes(self, changes, skip_updates=None):
        if changes:
            logger.debug('changes:\n%s' % changes)
        status_logger.debug('[handle_changes]')
        self.updater.update_status(skip_updates, changes)

    # XXX: This is MPD-specific. Move it to the backend somehow?
    def handle_idle(self, event):
        """
        Event handler for idle events (changes to MPD state).
        """
        logger.debug('got an event...')
        if not self.skip_idle:
            self.handle_changes(self.backend.noidle())
            self.backend.idle()
        self.skip_idle = False

    @Command()
    def do_previous(self, event):
        self.backend.previous()

    @Command()
    def do_play(self, event):
        self.backend.play()
        self.progress_slider.Enable(True)

    @Command()
    def do_stop(self, event):
        self.backend.stop()

    @Command()
    def do_next(self, event):
        logger.debug('do_next')
        self.backend.next()

    @Command()
    def do_change_song(self, event):
        i = event.GetItem()
        song_id = i.GetData()
        self.backend.playid(song_id)

    @Command(skip_updates=set(['progress_slider']))
    def do_seek(self, event):
        logger.debug(event.GetEventType())
        slider = event.GetEventObject()
        self.backend.seek(slider.GetValue())

    @Command(skip_updates=set(['volume_slider']))
    def do_volume_set(self, event):
        logger.debug(event.GetEventType())
        slider = event.GetEventObject()
        self.backend.setvol(slider.GetValue())


# Add command methods
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


