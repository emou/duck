from duck.errors import BackendInitializeError, BackendConnectionError
try:
    import mpd
except ImportError:
    raise BackendInitializeError('Python mpd client library could not be found. '
                                 'Is python-mpd installed?')
import select
import socket

from duck.backend import BaseBackend
from duck.backend.mpd.idle import IdleThread
from duck.backend.mpd.playlist import Playlist
from duck.backend.mpd.song import Song
from duck.log import loggers
from threading import Event

idle_logger = loggers.idle
logger = loggers.main
status_logger = loggers.status

class Backend(BaseBackend):
    """
    A backend that talks to an MPD server.
    """

    default_options = {
        'host': 'localhost',
        'port': 6600,
    }

    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options', None)
        BaseBackend.__init__(self, *args, **kwargs)
        self.options = Backend.default_options.copy()
        self._last_status = None
        self.status = None
        if options:
            self.options.update(options)

    def initialize(self):
        self._connect()
        self._changes = None
        self.idle_request = Event()
        self.idle_request.clear()
        self.idle_thread = IdleThread(self)
        self.idle_thread.start()

    def _connect(self):
        self.client = mpd.MPDClient()
        try:
            self.client.connect(self.options['host'], self.options['port'])
        except (mpd.MPDError, socket.error) as e:
            msg = [
                'Could not connect to MPD Server at %(host)s:%(port)s.' % self.options,
                '%s.' % e,
                'Press OK to try again or Cancel to exit.',
            ]
            raise BackendInitializeError('\n'.join(msg))

    def __enter__(self):
        try:
            self._changes = self._noidle()
        except mpd.MPDConnectionError, e:
            raise BackendConnectionError("MPDConnection error: %s" % e)
        return self

    def __exit__(self, *args):
        self.idle()

    def last_changes(self):
        return self._changes

    def end_command(self):
        self.idle()

    def add_artist(self, artist):
        for f in self.client.list('file', 'artist', artist):
            self.client.add(f)

    def replace_artist(self, artist):
        self.clear()
        self.add_artist(artist)

    def add_album(self, album):
        pass

    def play(self, song_id=None):
        if song_id:
            return self.client.play(song_id)
        else:
            return self.client.play()

    def playid(self, song_id):
        return self.client.play(song_id)

    def pause(self):
        return self.client.pause()

    def stop(self):
        return self.client.stop()

    def next(self):
        return self.client.next()

    def previous(self):
        return self.client.previous()

    def seek(self, value):
        return self.client.seekid(self.current_song.id, value)

    def setvol(self, value):
        return self.client.setvol(value)

    def clear(self):
        return self.client.clear()

    def list(self, *args):
        return self.client.list(*args)

    # {{ Methods dealing with idle mode

    def idle(self):
        """
        Main thread marks it's idle.
        Happens-before: noidle.
        """
        self._isidle=True
        self.client.send_idle()
        idle_logger.debug('[idle]')
        self.idle_request.set()

    def _wait_for_idle(self):
        """
        Notification thread blocks on socket.
        """
        idle_logger.debug('[idle-wait] Waiting for idle_request...')
        self.idle_request.wait()
        idle_logger.debug('[idle-poll] Polling for changes...')
        select.select([self.client], [], [])
        self.idle_request.clear()

    def _idle_wokeup(self):
        """
        Notification thread woke up.
        """
        pass

    def _noidle(self):
        """
        Main thread marks it's not idle anymore.
        """
        idle_logger.debug('[noidle] Fetching changes and cancelling idle mode...')
        self.client.send_noidle()
        self._isidle=False
        return self.client.fetch_idle()

    # }} Methods dealing with idle mode

    @property
    def current_song(self):
        song_dict = self.client.currentsong()
        if song_dict:
            logger.debug(song_dict)
            return Song(song_dict)

    def get_status(self):
        self._last_status = self.status
        self.status = self.client.status()
        return self.status

    def playlist_changes(self):
        if self.status and self._last_status:
            # TODO: check this:
            # self._last_status['playlistlength'] != self.status['playlistlength']
            # and optimize refresh
            # self.client.plchangesposid(self._last_status['playlist'])
            return []
        return []

    @property
    def playlist(self):
        return Playlist(self.client.playlistinfo())

    @property
    def playlistid(self):
        return self.client.playlistid()

    # {{ Computed fields

    @property
    def volume(self):
        return int(self.status['volume'])

    @property
    def elapsed_time(self):
        return int(self.status['time'].split(':')[0])

    @property
    def time(self):
        return int(self.status['time'].split(':')[1])

    # }} Computed fields

    def disconnect(self):
        try:
            self.client.close()
        except (mpd.MPDError, socket.error):
            pass
        try:
            self.client.disconnect()
        except (mpd.MPDError, IOError):
            # This one is corrupted. Use a new one.
            self.client = mpd.MPDClient()

