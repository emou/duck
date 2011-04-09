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
from threading import Lock

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
        self.lock = Lock()
        self.idle_lock = Lock()
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
        self.lock.acquire()
        #self.idle_lock.acquire()
        self.idle()

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
        """
        Main thread marks it's idle.
        """
        self.client.send_idle()
        self.is_idle = True
        self.idle_lock.acquire()
        self.lock.release()
    
    def idle_wait(self):
        """
        Notification thread blocks on socket.
        """
        self.lock.acquire()
        self.lock.release()
        select.select([self.client], [], [])
    
    def idle_wokeup(self):
        """
        Notification thread woke up. 
        """
        self.idle_lock.acquire()
        self.idle_lock.release()
 
    def noidle(self):
        """
        Main thread marks it's not idle anymore.
        """
        print 'noidle...'
        self.lock.acquire()
        self.idle_lock.release()
        self.is_idle = False
        print 'Sending noidle...'
        self.client.send_noidle()
        print 'Sent noidle.'
        print 'Reading idle data...'
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

