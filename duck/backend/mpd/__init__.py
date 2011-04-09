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
from duck.errors import BackendInitializeError
from duck.utils import Calculations
from duck.backend.mpd.song import Song
from threading import Event

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
                'Are your host/port settings correct?',
            ]
            raise BackendInitializeError('\n'.join(msg))
        self.idle_request = Event()
        self.idle_request.clear()
        self.idle_ready = Event()
        self.idle_ready.clear()

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

    # Thread-safe.
    def idle(self):
        """
        Main thread marks it's idle.
        """
        print '\nsending idle'
        self.client.send_idle()
        print 'setting idle_request to true...\n'
        self.idle_request.set()

    # Thread-safe.
    def idle_wait(self):
        """
        Notification thread blocks on socket.
        """
        print 'wait for idle_request...'
        self.idle_request.wait()
        self.idle_request.clear()
        print 'Polling for changes...'
        select.select([self.client], [], [])

    # Thread-safe.
    def idle_wokeup(self):
        """
        Notification thread woke up.
        """
        pass

    # Thread-safe.
    def noidle(self):
        """
        Main thread marks it's not idle anymore.
        """
        self.client.send_noidle()
        print 'Fetching changes and cancelling idle mode...'
        data = self.client.fetch_idle()
        return data

    def fetch_changes(self):
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
            # This guy is corrupted. Use a new one.
            self.client = MPDClient()

