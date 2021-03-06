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
        self.album = kwargs.pop('album')
        self.time = kwargs.pop('time', 30)
    
    @property
    def id(self):
        return id(self)


class PlaylistMock(object):
    def __init__(self, songs=None):
        if songs is None:
            self.songs = [
                SongMock(pos=0, artist='Morphine', title='Sharks',
                         album='Yes', time=300),
                SongMock(pos=1, artist='Pearl Jam', title='Alive',
                         album='Ten', time=200),
                SongMock(pos=2, artist='3 Doors Down', title='Loser',
                         album='The Better Life', time=400),
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
 
    def current_song(self, sync=False):
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
        song_pos = self.backend.current_song().pos

        self.assertEqual(playlist.GetItemText(0, 1),
                         self.backend.playlist.songs[0].artist)

        self.assertTrue(self.backend.initialized)

        self.assertEqual(self.window.volume_slider.GetValue(),
                         self.backend.volume)
        playlist.GetItemFont(song_pos).GetWeight()
        self.assertEqual(playlist.GetItemFont(song_pos).GetWeight(),
                        wx.BOLD)

        self.assertEqual(playlist.GetItemState(song_pos, wx.LIST_STATE_FOCUSED),
                         wx.LIST_STATE_FOCUSED)

    def test_initialize_error(self):
        def err():
            raise BackendInitializeError()
        self.backend.initialize = err
        self.assertRaises(FatalError, self.window.initialize)

if __name__ == '__main__':
    unittest.main()
