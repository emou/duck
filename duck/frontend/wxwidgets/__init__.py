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
status_logger = loggers.status

class ChangesEvent(wx.PyEvent):
    """
    An event representing an MPD status change.
    """

    REFRESH_EVT_ID = wx.NewId()

    def __init__(self, changes):
        wx.PyEvent.__init__(self)
        self.SetEventType(self.REFRESH_EVT_ID)
        self._changes = changes

    def get_changes(self):
        return self._changes

def command(func):
    def cmd_func(window, *args, **kwargs):
        logger.debug('[begin] command %s' % func.__name__)
        with window.backend as b:
            b.frontend.async_refresh(b.last_changes())
            ret = func(window, *args, **kwargs)
        logger.debug('[end] command %s' % func.__name__)
        return ret
    return cmd_func

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
        self.current_song = None

        # The wx.App object must be created first!
        self.NORMAL_FONT = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL, wx.NORMAL)
        self.BOLD_FONT   = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL, wx.BOLD)

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
            self.playlist.refresh()
        if state != 'stop':
            self.update(skip_updates)

    def reload_library(self):
        for c in [self.win.album_list, self.win.song_list]:
            c.DeleteAllItems()
        self.win.artist_list.refresh()

    def common_update(self):
        """
        Called everytime something changes.
        """
        status_logger.debug('[common_update]')
        song = self.win.backend.current_song

        if self.current_song != long(song.pos):
            if self.current_song is not None:
                self.win.playlist.SetItemFont(self.current_song, self.NORMAL_FONT)
            self.win.SetTitle('%s - %s' % (song.artist, song.title))
            self.win.status_bar.SetStatusText('%s - %s' % (song.artist, song.title))
            self.current_song = long(song.pos)
            self.win.playlist.SetItemFont(self.current_song, self.BOLD_FONT)
            self.win.playlist.SetItemState(self.current_song, wx.LIST_STATE_FOCUSED, wx.LIST_STATE_FOCUSED)
            self.win.playlist.EnsureVisible(self.current_song)

        playlist_changes = self.win.backend.playlist_changes()
        if playlist_changes:
            self.playlist.refresh()

        if self.win.backend.status['state'] == 'play':
            self.win.progress_timer.Start(1000, oneShot=False)


class EventHandler(object):
    """
    An object that handles window events.
    """

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
        self.stop_timer()
        self.win.progress_slider.Enable(False)


class DuckWindow(MainWindow):

    def __init__(self, *args, **kwargs):
        assert 'backend' in kwargs
        self.backend = kwargs.pop('backend')
        MainWindow.__init__(self, *args, **kwargs)

        for c in [self.playlist, self.artist_list, self.album_list]:
            c.initialize(self)

        self.updater = WindowUpdater(self)
        self.handler = EventHandler(self)
        self.progress_timer = wx.Timer(self, wx.ID_ANY)

        self.song_list.InsertColumn(0, 'Song')

        # Event bindings
        self.Connect(-1, -1, ChangesEvent.REFRESH_EVT_ID, self.refresh)
        self.Bind(wx.EVT_TIMER, self.updater.update_progress)
        self.progress_slider.Bind(wx.EVT_SLIDER, self.do_seek)
        self.volume_slider.Bind(wx.EVT_SLIDER, self.do_volume_set)

    def initialize(self):
        self.progress_slider.SetValue(0)
        self.notebook.ChangeSelection(0)
        self.backend.initialize()
        self.playlist.refresh()
        self.updater.reload_library()
        self.updater.update_status()
        self.backend.idle()

    def handle_changes(self, changes, skip_updates=None):
        print 'changeS: %s' % changes
        if changes:
            logger.debug('changes:\n%s' % changes)
        status_logger.debug('[handle_changes]')
        self.updater.update_status(skip_updates, changes)

    def refresh(self, event):
        with self.backend as b:
            changes = event.get_changes()
            self.handle_changes(changes)

    @command
    def do_filter_artist(self, event):
        selected_artist = event.GetItem().GetText()
        self.album_list.load(sorted(self.backend.list('album', 'artist', selected_artist)))

        self.song_list.DeleteAllItems()

        for row, a in enumerate(
            sorted(self.backend.list('title', 'artist', selected_artist))):

                item = wx.ListItem()
                item.SetId(row + 1)
                item.SetText(a)
                self.song_list.InsertItem(item)
        self.song_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    @command
    def do_filter_album(self, event):
        self.song_list.DeleteAllItems()
        selected_album = event.GetItem().GetText()
        for row, a in enumerate(
            sorted(self.backend.list('title', 'album', selected_album))):

                item = wx.ListItem()
                item.SetId(row + 1)
                item.SetText(a)
                self.song_list.InsertItem(item)
        self.song_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)

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
    def do_change_song(self, event):
        self.backend.playid(event.GetItem().GetData())

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

    @command
    def do_add_artist(self, event):
        self.backend.add_artist(event.GetItem().GetText())

    @command
    def do_add_album(self, event):
        self.backend.add_album(event.GetItem().GetText())

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


