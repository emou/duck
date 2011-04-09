try:
    from mpd import MPDClient, MPDError
except ImportError:
    raise BackendInitializeError('Python mpd client library could not be found. '
                                 'Is python-mpd installed?')
import socket

import duck.backend
from duck.backend import BaseBackend
from duck.errors import BackendInitializeError
from duck.utils import Calculations
from duck.backend.mpd.song import Song

class Backend(BaseBackend):
    """
    A backend that talks to an MPD server.
    """

    default_options = {
        'host': 'localhost',
        'port': 6600,
    }

    def __init__(self, options=None):
        self.options = Backend.default_options.copy()
        if options:
            self.options.update(options)
        self.client = MPDClient()
        try:
            self.client.connect(self.options['host'],
                                self.options['port'])
        except (MPDError, socket.error) as e:
            msg = [
                'Could not connect to MPD Server at '
                '%(host)s:%(port)s.' % self.options,
                'Returned error was: %s.' % e,
                'Did you forget to install or start the mpd server?',
            ]
            raise BackendInitializeError('\n'.join(msg))

    def play(self):
        self.client.play()

    def pause(self):
        self.client.pause()

    def stop(self):
        self.client.stop()

    def next(self):
        self.client.next()

    def previous(self):
        self.client.previous()

    def seek(self, xpercent):
        self.client.seek(self.current_song.id,
                         Calculations.intpercent(xpercent, self.current_song.time))
    
    def idle(self):
        import select
        self.client.send_idle()
        select.select([self.client], [], [])
        return self.client.fetch_idle()

    @property
    def current_song(self):
        return Song(self.client.currentsong())

    def disconnect(self):
        try:
            self.client.close()
        except (MPDError, socket.error):
            pass
        try:
            self.client.disconnect()
        except (MPDError, IOError):
            # Just use a new client
            self.client = MPDClient()

