from duck.utils import Duration
import os

class Song(object):
    """
    A class representing a song in the MPD database.
    """

    __slots__ = ('id', 'album', 'artist', 'filepath', 'pos', 'title', 'time')

    _cache = {}

    def __new__(typ, song_dict):
        _id = song_dict['id']
        try:
            return typ._cache[_id]
        except KeyError:
            self = object.__new__(typ)
            self.id = _id

        self.title = song_dict.get('title',
            os.path.splitext(os.path.split(song_dict.get('file', ''))[1])[0]
        )
        self.artist = song_dict.get('artist', '')
        self.album = song_dict.get('album', '')
        self.time = Duration(seconds=int(song_dict.get('time', 0)))
        self.pos = int(song_dict['pos'])
        self.filepath = song_dict['file']

        typ._cache[self.id] = self

        return self
