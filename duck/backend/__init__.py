"""
This modules contains the base class for a Backend:
an object that does the actual control.
At this point we don't care what it actually does.
It could for example:
    * Talk to a server, like MPD
    * Run an external program, like mplayer
    * Print pages on a printer :)
"""

class BaseBackend(object):
    """
    The base Backend object.
    """

    def play(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def next(self):
        raise NotImplementedError()

    def previous(self):
        raise NotImplementedError()

class BackendError(Exception):
    """
    A base error in the backend.
    """
    errcode = 255

class BackendInitializeError(BackendError):
    """
    An error during backend initialization, i.e.
    could not connect to server, could not import
    a module, etc.
    """
    errcode = 254

