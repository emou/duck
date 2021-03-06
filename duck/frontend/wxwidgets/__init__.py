from duck.errors import FrontendInitializeError
try:
    import wx
except ImportError:
    raise FrontendInitializeError('could not import wx: make sure wxpython is installed')
try:
    import pynotify
except ImportError:
    _NOTIFY = False
else:
    _NOTIFY = True
    pynotify.init("duck-player")


from duck.frontend import BaseFrontend
from duck.frontend.wxwidgets.events import ChangesEvent, BackendConnectedEvent
from duck.log import loggers
from duck.utils import Poller
from gui.noname import MainWindow

logger = loggers.main
status_logger = loggers.status

def command(func):
    def cmd_func(window, *args, **kwargs):
        logger.debug('[begin] command %s' % func.__name__)
        with window.backend as b:
            b.frontend.async_refresh(b.last_changes())
            ret = func(window, *args, **kwargs)
        logger.debug('[end] command %s' % func.__name__)
        return ret
    return cmd_func

class DuckWindow(MainWindow):

    updates = set([
        'progress_slider',
        'volume_slider',
    ])

    def try_to_initialize_backend(self):
        self.backend.initialize()

    def handle_backend_error(self, e):
        logger.error('Error starting up backend: %s.' % e)

    def handle_backend_success(self, res):
        logger.debug('Connected!')
        wx.PostEvent(self, BackendConnectedEvent())

    def connected(self, evt):
        self.playlist.refresh()
        self.reload_library()
        self.update_status()
        self.backend.idle()

    def __init__(self, *args, **kwargs):
        assert 'backend' in kwargs
        self.backend = kwargs.pop('backend')
        MainWindow.__init__(self, *args, **kwargs)

        self.progress_timer = wx.Timer(self, wx.ID_ANY)
        self.state = None
        self.current_song = None

        # Event bindings
        self.Connect(-1, -1, ChangesEvent.CHANGES_EVT_ID, self.refresh)
        self.Connect(-1, -1, BackendConnectedEvent.BACKEND_CONNECTED_EVT_ID, self.connected)
        self.Bind(wx.EVT_TIMER, self.update_progress)
        self.Bind(wx.EVT_MENU, self.do_rescan_database, self.item_rescan)
        self.progress_slider.Bind(wx.EVT_SLIDER, self.do_seek)
        self.volume_slider.Bind(wx.EVT_SLIDER, self.do_volume_set)

        self.initialize_poller = Poller(
            try_func=self.try_to_initialize_backend,
            exception_handler=self.handle_backend_error,
            success_handler=self.handle_backend_success,
        )

    def initialize(self):
        self.playlist.set_search_field(self.playlist_search)
        self.artist_list.set_search_field(self.library_search_field)
        self.progress_slider.SetValue(0)
        self.notebook.ChangeSelection(0)
        if _NOTIFY:
            self.notification = pynotify.Notification('duck music player')
        else:
            self.notification = None

        for c in [self.playlist, self.artist_list, self.album_list, self.song_list]:
            c.initialize(self)

        self.initialize_poller.start()

    def handle_changes(self, changes, skip_updates=None):
        if changes:
            logger.debug('changes:\n%s' % changes)
        status_logger.debug('[handle_changes]')
        self.update_status(skip_updates, changes)

    def refresh(self, event):
        with self.backend:
            changes = event.get_changes()
            self.handle_changes(changes)

    @command
    def do_change_song(self, songid):
        """
        Tell the backend to change to song with `songid` in the current
        playlist.
        """
        self.backend.playid(songid)

    @command
    def do_filter_artist(self, selected_artist):
        self.album_list.load(sorted(self.backend.list(
            'album', 'artist', selected_artist)))
        self.song_list.load(sorted(self.backend.list(
            'title', 'artist', selected_artist)))

    @command
    def do_filter_album(self, event):
        selected_album = event.GetItem().GetText()
        self.song_list.load(sorted(self.backend.list(
            'title', 'album', selected_album)))

    @command
    def do_previous(self, event):
        self.backend.previous()

    @command
    def do_play(self, event):
        if self.backend.playlist.songs:
            self.backend.play()
            self.progress_slider.Enable(True)
        else:
            # TODO: Show a dialog with message
            print 'Playlist is empty'

    @command
    def do_pause(self, event):
        self.backend.pause()

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

    @command
    def do_volume_set(self, event):
        logger.debug('volume set')
        logger.debug(event.GetEventType())
        val = event.GetEventObject().GetValue()
        self.backend.setvol(val)

    @command
    def do_clear(self, event):
        self.backend.clear()
        wx.PostEvent(self, ChangesEvent(['playlist']))

    @command
    def do_add_artist(self, event):
        self.backend.add_artist(event.GetItem().GetText())
        wx.PostEvent(self, ChangesEvent(['playlist']))

    @command
    def do_add_album(self, event):
        self.backend.add_album(event.GetItem().GetText())
        wx.PostEvent(self, ChangesEvent(['playlist']))

    @command
    def do_rescan_database(self, event):
        self.backend.rescan_database()

    def on_play(self):
        self.progress_slider.Enable(True)

    def on_stop(self):
        self.stop_timer()
        self.progress_slider.SetValue(0)
        self.progress_slider.Enable(False)

    def stop_timer(self):
        if self.progress_timer.IsRunning():
            self.progress_timer.Stop()

    def on_pause(self):
        self.stop_timer()
        self.progress_slider.Enable(False)

    def update(self, skip_updates=None):
        status_logger.debug('[update]')
        new_song = self.backend.current_song(sync=True)

        if self.current_song is None or self.current_song.id != new_song.id:
            self.playlist.change_song(self.current_song, new_song)
            self.current_song = new_song
            self.SetTitle('%s - %s' % (new_song.artist, new_song.title))
            self.status_bar.SetStatusText(
                '%s - %s' % (new_song.artist, new_song.title)
            )
            if _NOTIFY:
                self.notification.update(
                    'Now Playing',
                    '%s - %s' % (new_song.artist, new_song.title)
                )
                self.notification.show()

        playlist_changes = self.backend.playlist_changes()
        if playlist_changes:
            self.playlist.refresh()

        if self.backend.status['state'] == 'play':
            self.progress_timer.Start(1000, oneShot=False)
        for u in self.updates - set(skip_updates or []):
            getattr(self, 'update_' + u)()

    def update_progress_slider(self):
        self.progress_slider.SetRange(0, self.backend.time)
        self.progress_slider.SetValue(self.backend.elapsed_time)

    def update_volume_slider(self):
        self.volume_slider.SetValue(self.backend.volume)

    def update_progress(self, event):
        self.progress_slider.SetValue(self.progress_slider.GetValue() + 1)

    def update_status(self, skip_updates=None, changes=None):
        status_logger.debug('[update_status]')
        state = self.backend.get_status()['state']
        getattr(self, 'on_' + state)()
        self.state = state
        if changes and 'playlist' in changes:
            self.playlist.refresh()
        if state != 'stop':
            self.update(skip_updates)

    def reload_library(self):
        for c in [self.album_list, self.song_list]:
            c.DeleteAllItems()
        self.artist_list.refresh()


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
        self.main_window.initialize()
        self.main_window.Show()
        self.application.SetTopWindow(self.main_window)
        return self.application.MainLoop()

    def async_refresh(self, changes=None):
        wx.PostEvent(self.main_window, ChangesEvent(changes))

