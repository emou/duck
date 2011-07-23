import unittest
import wx

from duck.backend import BaseBackend
from duck.errors import BackendInitializeError, FatalError
from duck.frontend.wxwidgets import Frontend, DuckWindow


class SongMock(object):
    def __init__(self, **kwargs):
        self.pos = kwargs.pop('pos')
        self.artist = kwargs.pop('artist')
        self.title = kwargs.pop('title')
        self.time = kwargs.pop('time', 30)
    
    @property
    def id(self):
        return id(self)


class PlaylistMock(object):
    def __init__(self, songs=None):
        if songs is None:
            self.songs = [
                SongMock(pos=0, artist='Morphine', title='Sharks', time=300),
                SongMock(pos=1, artist='Pearl Jam', title='I am alive', time=200),
            ]
        else:
            self.songs = songs


class BackendMock(BaseBackend):

    def __init__(self, *args, **kwargs):
        BaseBackend.__init__(self, *args, **kwargs)
        self._idle = False
        self.initialized = False

    def idle(self):
        self._idle = True
    
    def initialize(self):
        self.initialized = True
    
    def list(self, what):
        if what=='artist':
            return ['Morphine']
        raise NotImplementedError()
    
    def playlist_changes(self):
        return []
    
    def get_status(self):
        self.status =  {
            'state': 'play',
        }
        return self.status

    @property
    def time(self):
        return 20
    
    @property
    def elapsed_time(self):
        return 5
    
    @property
    def volume(self):
        return 75
 
    @property
    def current_song(self):
        return self.playlist.songs[1]
 
    @property
    def playlist(self):
        try:
            return self._playlist
        except AttributeError:
            self._playlist = PlaylistMock()
        return self._playlist


class FrontendTestCase(unittest.TestCase):

    def setUp(self):
        self.frontend = Frontend(BackendMock)

    def test_frontend_creation(self):
        """
        Just trigger the running of setUp.
        """
        pass


class DuckWindowTestCase(unittest.TestCase):

    def setUp(self):
        self.app = wx.App()
        self.frontend = Frontend(BackendMock)
        self.backend = self.frontend.backend
        self.window = DuckWindow(None, backend=self.frontend.backend)
    
    def test_frontend_initialize(self):
        self.assertFalse(self.backend.initialized)

        self.window.initialize()

        playlist = self.window.playlist
        song_pos = self.backend.current_song.pos

        self.assertEqual(playlist.GetItem(0, 1).GetText(),
                         self.backend.playlist.songs[0].artist)

        self.assertTrue(self.backend.initialized)

        self.assertEqual(self.window.volume_slider.GetValue(),
                         self.backend.volume)

        self.assertEqual(playlist.GetItemFont(song_pos).GetWeight(),
                        wx.BOLD)

        self.assertEqual(playlist.GetItemState(song_pos, wx.LIST_STATE_FOCUSED),
                         wx.LIST_STATE_FOCUSED)

        # Assert current song is visible. A bit of a bogus test as we have a
        # low number of songs, but still...
        self.assertTrue(playlist.GetViewRect().InsideRect(playlist.GetItemRect(song_pos)))
    
    def test_initialize_error(self):
        def err():
            raise BackendInitializeError()
        self.backend.initialize = err

        self._dialog_showed = False
        def click_after_show(show):
            def _clickAfter(dialog, *args, **kwargs):
                """
                Don't actually show the dialog.
                Just process the event.
                """
                self._dialog_showed = True
                clickEvent = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                             wx.ID_CANCEL)
                dialog.ProcessEvent(clickEvent)
            return _clickAfter

        wx.MessageDialog.ShowModal = click_after_show(wx.MessageDialog.ShowModal)

        self.assertRaises(FatalError, self.window.initialize)
        self.assertTrue(self._dialog_showed)

if __name__ == '__main__':
    unittest.main()
