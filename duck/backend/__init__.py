"""
A base class for a backend.
"""

class BaseBackend(object):
    """
    The base Backend object.
    """

    def __init__(self, frontend):
        self.frontend = frontend

    def initialize(self):
        """
        Should implement backend initializiation, like connecting to a
        database or a musical server, setting up some initial state, etc.
        """
        raise NotImplementedError()

    def fetch_changes(self):
        """
        Fetch changes. Should return a list of types of changes.
        Possible values in the list are:
            * 'playlist' when songs are added/deleted from the playlist
            * 'player' when player is paused/stopped/started
        """
        raise NotImplementedError()

    def idle(self):
        """
        The frontend should call this method to indicate it is idle,
        so it can recieve "push" notifications when state changes.

        Makes sense for server backends.
        """
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

    def __enter__(self):
        """
        Called when starting a conversation with the backend. Could be thought
        of as marking the beginning of a "transaction".
        """
        raise NotImplementedError()

    def __exit__(self, *args):
        """
        End a conversation with the backend. Could be thought of as marking the
        end of a "transaction".
        """
        raise NotImplementedError()
