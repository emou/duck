try:
    from mpd import MPDClient, MPDError, PendingCommandError, ConnectionError
except ImportError:
    raise BackendInitializeError('Python mpd client library could not be found. '
                                 'Is python-mpd installed?')
import select
import socket
import time

import duck.backend
from duck.backend import BaseBackend
from duck.errors import BackendInitializeError, BackendError
from duck.utils import Calculations
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
        if options:
            self.options.update(options)

    def initialize(self):
        self._connect()
        self.idle_request = Event()
        self.idle_request.clear()
        self.idle_thread = IdleThread(self)
        self.idle_thread.start()

    def _connect(self):
        self.client = MPDClient()
        try:
            self.client.connect(self.options['host'], self.options['port'])
        except (MPDError, socket.error) as e:
            msg = [
                'Could not connect to MPD Server at '
                '%(host)s:%(port)s.' % self.options,
                'Returned error was: %s.' % e,
                'Is the mpd server running?',
                'Are your host/port settings correct?',
            ]
            raise BackendInitializeError('\n'.join(msg))

    def start_command(self):
        changes = self._noidle()
        self.frontend.async_refresh(changes)

    def end_command(self):
        self.idle()

    def play(self, song_id=None):
        if song_id:
            return self.client.play(song_id)
        else:
            return self.client.play()

    def playid(self, song_id):
        return self.client.playid(song_id)

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

    # {{ Methods dealing with idle mode

    def idle(self):
        """
        Main thread marks it's idle.
        """
        self._is_idle = True
        self.client.send_idle()
        idle_logger.debug('[idle]')
        self.idle_request.set()

    def _idle_wait(self):
        """
        Notification thread blocks on socket.
        """
        idle_logger.debug('[idle-wait] Waiting for idle_request...')
        self.idle_request.wait()
        self.idle_request.clear()
        idle_logger.debug('[idle-poll] Polling for changes...')
        select.select([self.client], [], [])

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
        self._is_idle = False
        return self.client.fetch_idle()

    def fetch_changes(self):
        changes = self._noidle()
        self.idle()
        return changes

    # }} Methods dealing with idle mode

    @property
    def current_song(self):
        song_dict = self.client.currentsong()
        if song_dict:
            logger.debug(song_dict)
            return Song(song_dict)

    def get_status(self):
        self.status = self.client.status()
        return self.status

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
        except (MPDError, socket.error):
            pass
        try:
            self.client.disconnect()
        except (MPDError, IOError):
            # This guy is corrupted. Use a new one.
            self.client = MPDClient()

