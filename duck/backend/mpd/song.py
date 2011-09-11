from duck.utils import Duration
import os

class Song(object):
    """
    A class representing a song in the MPD database.
    """

    __slots__ = ('id', 'album', 'artist', 'filepath', 'pos', 'title', 'time')

    def __init__(self, song_dict):
        self.id = song_dict['id']
        self.title = song_dict.get('title',
            os.path.splitext(os.path.split(song_dict.get('file', ''))[1])[0]
        )
        self.artist = song_dict.get('artist', '')
        self.album = song_dict.get('album', '')
        self.time = Duration(seconds=int(song_dict.get('time', 0)))
        self.pos = int(song_dict['pos'])
        self.filepath = song_dict['file']


