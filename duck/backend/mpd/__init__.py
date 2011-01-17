import duck.backend
from duck.backend import BaseBackend, BackendInitializeError
try:
    from mpd import MPDClient, MPDError
except ImportError:
    raise BackendInitializeError("python mpd client library could not be found. "
                                 "Is python-mpd installed?\n")
import socket

class Backend(BaseBackend):
    """
    A backend that talks to an MPD server.
    """

    default_options = {'host': 'localhost',
                       'port': 6600,}

    def __init__(self, options=None):
        self.options = Backend.default_options.copy()
        if options:
            self.options.update(options)
        self.client = MPDClient()
        try:
            self.client.connect(self.options['host'],
                                self.options['port'])
        except (MPDError, socket.error) as e:
            raise BackendInitializeError("Could not connect to MPD Server at %s:%s.\n"
                                         "Returned error was:\n%s" % (self.options['host'],
                                                                      self.options['port'],
                                                                     e))

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
