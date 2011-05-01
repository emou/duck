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
from duck.log import loggers
from threading import Event

idle_logger = loggers.idle
logger = loggers.main

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

    def seek(self, value):
        self.client.seek(self.current_song.id, value)

    def setvol(self, value):
        self.client.setvol(value)

    # {{ Methods dealing with idle mode and thread synchronization.

    def idle(self):
        """
        Main thread marks it's idle.
        """
        idle_logger.debug('\nsending idle')
        self.client.send_idle()
        idle_logger.debug('setting idle_request to true...\n')
        self.idle_request.set()

    def idle_wait(self):
        """
        Notification thread blocks on socket.
        """
        idle_logger.debug('wait for idle_request...')
        self.idle_request.wait()
        self.idle_request.clear()
        idle_logger.debug('Polling for changes...')
        select.select([self.client], [], [])

    def idle_wokeup(self):
        """
        Notification thread woke up.
        """
        pass

    def noidle(self):
        """
        Main thread marks it's not idle anymore.
        """
        self.client.send_noidle()
        idle_logger.debug('Fetching changes and cancelling idle mode...')
        data = self.client.fetch_idle()
        return data

    def fetch_changes(self):
        return self.client.fetch_idle()

    # }}

    @property
    def current_song(self):
        song_dict = self.client.currentsong()
        if song_dict:
            logger.debug(song_dict)
            return Song(song_dict)
    
    def get_status(self):
        self.status = self.client.status()
        self.memo = {}
        return self.status
 
    @property
    def elapsed_time(self):
        return int(self.status['time'].split(':')[0])

    @property
    def time(self):
        return int(self.status['time'].split(':')[1])

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

