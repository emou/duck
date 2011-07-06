from duck.backend.mpd.song import Song

class Playlist(object):
    """
    An object hodling the current playlist.
    """
    def __init__(self, playlist_data):
        self.songs = sorted(map(Song, playlist_data),
                            key=lambda x: x.pos,
                            reverse=True)

    def __iter__(self):
        return self
