"""
This modules contains the base class for a Backend:
an object that does the actual control.
At this point we don't care what it actually does.
In theory it could for example:
    * Talk to a server, like MPD
    * Run an external program, like mplayer
    * Use a local playing engine
"""

class BaseBackend(object):
    """
    The base Backend object.
    """

    def __init__(self, frontend):
        self.frontend = frontend
    
    def fetch_changes(self):
        raise NotImplementedError()

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

