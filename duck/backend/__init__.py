"""
A base class for a backend.
"""

from duck.errors import BackendNoStoredValueError

class _StoredValueClass(object):
    """
    Use this decorator to transparently implement methods that take a `sync`
    parameter.

    In the body of the method, just calculate the synced value.  The decorator
    will take care to implement everything else that's needed to implement the
    behaviour that the BaseBackend interface defines.
    """
    _memo = {}

    def __call__(self, method):
        def stored_value_method(obj, *args, **kwargs):
            sync = kwargs.pop('sync', False)
            if sync:
                self._memo[method] = method(obj, *args, **kwargs)
            try:
                return self._memo[method]
            except KeyError:
                raise BackendNoStoredValueError()
        return stored_value_method

# Singleton-Simpleton
stored_value = _StoredValueClass()

class BaseBackend(object):
    """
    The abstract base Backend object.
    """

    def __init__(self, frontend):
        """
        Object initialization. Please put "heavier" initialization actions
        in the `initialize` method.
        """
        self.frontend = frontend

    def initialize(self):
        """
        Derived classes should should implement backend initializiation here.
        This might include connecting to a database, a musical server or other
        initial setup.
        """
        raise NotImplementedError()

    def fetch_changes(self):
        """
        Should return a list of types of changes that have occured.
        Possible values in the list are:
            * `playlist` when songs are added/deleted from the playlist
            * `player` when player is paused/stopped/started

        Makes sense for server backends. To be used in conjuction with the
        `idle` method:
            The client goes `idle` until it recieves notification.
            It then blocks inside the `idle` method. When it unblocks it calls
            this method asking for *what* has changed.
        """
        raise NotImplementedError()

    def idle(self):
        """
        The frontend calls this method to indicate it is idle, so it can
        recieve "push" notifications when state changes.

        Makes sense for server backends. It can safely be a `noop`.
        """
        pass

    def play(self, song_pos=None):
        """
        Start of playing music. Resume if paused.

        If `pos` is given, play the song at that position.
        Otherwise just resume play or play a default song in the playlist.
        """
        raise NotImplementedError()

    def playid(self, song_id=None):
        """
        Play the song with the given id, which is a unique identifier for the
        song.
        """
        pass

    def pause(self):
        """
        Pause playing of music.
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop the playing of music.
        """
        raise NotImplementedError()

    def seek(self, pos):
        """
        Seek at position `pos` in the current song.
        """
        raise NotImplementedError()

    def setvol(self, val):
        """
        Set the volume to a `val` which should be a number between 0 and 100.
        """
        raise NotImplementedError()

    def clear(self):
        """
        Clear the current playlist.
        """
        raise NotImplementedError()

    def list(self, q_type):
        """
        Query the database (if any).

        Possible query types (`q_type`):
            * 'artist'
            * 'song'
            * 'album'

        Returns a list of the songs matching the query.
        """
        raise NotImplementedError()

    def next(self):
        """
        Implements changing to the next track in the playlist.
        """
        raise NotImplementedError()

    def previous(self):
        """
        Implements changing to the previous track in the current playlist.
        """
        raise NotImplementedError()

    def remove_song(self, songid):
        """
        Implements removing song with `songid` from the current playlist.
        """
        raise NotImplementedError()


    def __enter__(self):
        """
        Called when starting a conversation with the backend. Could be thought
        of as marking the beginning of a "transaction".

        It must put the client out of `idle` state.

        Can safely be a noop if not needed.
        """
        pass

    def __exit__(self, *args):
        """
        Called to end conversation with the backend.
        Could be thought of as marking the end of a "transaction".

        It must put the client back into `idle` state.

        Can safely be a noop if not needed.
        """
        pass

    def last_changes(self):
        """
        Returns the changes that might have occured while calling __enter__.

        The flow is like the following:

            with backend:
                # Process any changes gotten while switching out from `idle` mode.
                backend.last_changes()

        Can safely be a noop if not needed.
        """
        pass

    def add_artist(self, artist):
        """
        Add all of an artist's tracks to the current playlist.
        """
        raise NotImplementedError()

    def replace_artist(self, artist):
        """
        Replaces the current playlist with all of artist's tracks.
        """
        raise NotImplementedError()


    def current_song(self, sync=False):
        """
        Returns the current song.

        `sync` specifies wheter we should query the server (if any) or use a
        stored value.

        If `sync` is False and there is no stored value the implementing class should
        raise NoPreviousValueError.
        """
        raise NotImplementedError()
