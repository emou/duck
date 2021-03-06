from duck.backend.mpd.song import Song


class Playlist(object):
    """
    An object hodling the current playlist.
    """
    def __init__(self, playlist_data):
        self.songs = map(Song, playlist_data)

    def __iter__(self):
        return iter(self.songs)
